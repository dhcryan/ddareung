import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import mysql.connector
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BikeDemandPredictor:
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """시계열 및 환경 특성 추출"""
        df = df.copy()
        df['collected_at'] = pd.to_datetime(df['collected_at'])
        
        # 시간 관련 특성
        df['hour'] = df['collected_at'].dt.hour
        df['day_of_week'] = df['collected_at'].dt.dayofweek
        df['month'] = df['collected_at'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_rush_hour'] = ((df['hour'].isin([8, 9, 18, 19]))).astype(int)
        
        # 계절 특성
        df['season'] = df['month'].apply(lambda x: 
            0 if x in [12, 1, 2] else  # 겨울
            1 if x in [3, 4, 5] else   # 봄
            2 if x in [6, 7, 8] else   # 여름
            3)  # 가을
        
        # 이전 시간대 데이터 (lag features)
        df = df.sort_values(['station_id', 'collected_at'])
        df['prev_1h_bikes'] = df.groupby('station_id')['park_cnt'].shift(1)
        df['prev_2h_bikes'] = df.groupby('station_id')['park_cnt'].shift(2)
        df['prev_3h_bikes'] = df.groupby('station_id')['park_cnt'].shift(3)
        
        # 변화율 특성
        df['bike_change_1h'] = df['park_cnt'] - df['prev_1h_bikes']
        df['bike_change_2h'] = df['park_cnt'] - df['prev_2h_bikes']
        
        # 사용률 특성
        df['usage_rate'] = (df['rack_cnt'] - df['park_cnt']) / df['rack_cnt']
        df['availability_rate'] = df['park_cnt'] / df['rack_cnt']
        
        return df
    
    def load_training_data(self, days: int = 30) -> Optional[pd.DataFrame]:
        """학습용 데이터 로드"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            
            query = """
            SELECT station_id, station_name, park_cnt, rack_cnt, 
                   station_lat, station_lng, collected_at
            FROM realtime_bike_status 
            WHERE collected_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ORDER BY station_id, collected_at
            """
            
            df = pd.read_sql(query, conn, params=(days,))
            conn.close()
            
            if df.empty:
                logger.warning("학습용 데이터가 없습니다.")
                return None
                
            logger.info(f"학습용 데이터 로드 완료: {len(df)}개 레코드")
            return df
            
        except Exception as e:
            logger.error(f"데이터 로드 오류: {e}")
            return None
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """학습용 데이터 전처리"""
        # 특성 추출
        df = self.extract_features(df)
        
        # 결측값 제거
        df = df.dropna()
        
        # 특성 컬럼 정의
        self.feature_columns = [
            'hour', 'day_of_week', 'month', 'is_weekend', 'is_rush_hour', 'season',
            'prev_1h_bikes', 'prev_2h_bikes', 'prev_3h_bikes',
            'bike_change_1h', 'bike_change_2h', 'usage_rate', 'availability_rate',
            'rack_cnt', 'station_lat', 'station_lng'
        ]
        
        # 특성과 타겟 분리
        X = df[self.feature_columns].values
        y = df['park_cnt'].values
        
        # 정규화
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, y
    
    def train_model(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """모델 학습"""
        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 모델 학습
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # 모델 평가
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        metrics = {
            'mae': mae,
            'rmse': rmse,
            'train_score': self.model.score(X_train, y_train),
            'test_score': self.model.score(X_test, y_test)
        }
        
        logger.info(f"모델 학습 완료 - MAE: {mae:.2f}, RMSE: {rmse:.2f}")
        return metrics
    
    def predict_demand(self, station_id: str, hours_ahead: int = 2) -> Optional[List[Dict]]:
        """수요 예측"""
        if not self.model:
            logger.error("모델이 학습되지 않았습니다.")
            return None
            
        try:
            # 현재 대여소 정보 조회
            conn = mysql.connector.connect(**self.db_config)
            
            query = """
            SELECT station_id, station_name, park_cnt, rack_cnt, 
                   station_lat, station_lng, collected_at
            FROM realtime_bike_status 
            WHERE station_id = %s 
            ORDER BY collected_at DESC 
            LIMIT 10
            """
            
            df = pd.read_sql(query, conn, params=(station_id,))
            conn.close()
            
            if df.empty:
                logger.warning(f"대여소 {station_id}의 데이터가 없습니다.")
                return None
            
            predictions = []
            
            for hour in range(1, hours_ahead + 1):
                # 예측 시점 계산
                future_time = datetime.now() + timedelta(hours=hour)
                
                # 최신 데이터 기반 특성 생성
                latest_data = df.iloc[0].copy()
                
                # 미래 시간 특성
                latest_data['hour'] = future_time.hour
                latest_data['day_of_week'] = future_time.weekday()
                latest_data['month'] = future_time.month
                latest_data['is_weekend'] = 1 if future_time.weekday() >= 5 else 0
                latest_data['is_rush_hour'] = 1 if future_time.hour in [8, 9, 18, 19] else 0
                
                # 계절 특성
                latest_data['season'] = 0 if future_time.month in [12, 1, 2] else \
                                     1 if future_time.month in [3, 4, 5] else \
                                     2 if future_time.month in [6, 7, 8] else 3
                
                # 이전 시간대 데이터 사용
                latest_data['prev_1h_bikes'] = df.iloc[0]['park_cnt'] if len(df) > 0 else 0
                latest_data['prev_2h_bikes'] = df.iloc[1]['park_cnt'] if len(df) > 1 else 0
                latest_data['prev_3h_bikes'] = df.iloc[2]['park_cnt'] if len(df) > 2 else 0
                
                # 변화율 계산
                latest_data['bike_change_1h'] = latest_data['park_cnt'] - latest_data['prev_1h_bikes']
                latest_data['bike_change_2h'] = latest_data['park_cnt'] - latest_data['prev_2h_bikes']
                
                # 사용률 계산
                latest_data['usage_rate'] = (latest_data['rack_cnt'] - latest_data['park_cnt']) / latest_data['rack_cnt']
                latest_data['availability_rate'] = latest_data['park_cnt'] / latest_data['rack_cnt']
                
                # 예측용 특성 벡터 생성
                feature_vector = np.array([[
                    latest_data['hour'], latest_data['day_of_week'], latest_data['month'],
                    latest_data['is_weekend'], latest_data['is_rush_hour'], latest_data['season'],
                    latest_data['prev_1h_bikes'], latest_data['prev_2h_bikes'], latest_data['prev_3h_bikes'],
                    latest_data['bike_change_1h'], latest_data['bike_change_2h'],
                    latest_data['usage_rate'], latest_data['availability_rate'],
                    latest_data['rack_cnt'], latest_data['station_lat'], latest_data['station_lng']
                ]])
                
                # 정규화
                feature_vector_scaled = self.scaler.transform(feature_vector)
                
                # 예측
                prediction = self.model.predict(feature_vector_scaled)[0]
                prediction = max(0, min(prediction, latest_data['rack_cnt']))  # 범위 제한
                
                predictions.append({
                    'station_id': station_id,
                    'station_name': latest_data['station_name'],
                    'predicted_time': future_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'hours_ahead': hour,
                    'predicted_bikes': int(prediction),
                    'current_bikes': int(latest_data['park_cnt']),
                    'total_racks': int(latest_data['rack_cnt']),
                    'predicted_availability': prediction / latest_data['rack_cnt']
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"예측 오류: {e}")
            return None
    
    def save_model(self, filepath: str):
        """모델 저장"""
        if self.model:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns
            }, filepath)
            logger.info(f"모델 저장 완료: {filepath}")
    
    def load_model(self, filepath: str):
        """모델 로드"""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
            logger.info(f"모델 로드 완료: {filepath}")
        except Exception as e:
            logger.error(f"모델 로드 오류: {e}")

if __name__ == "__main__":
    # 설정
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '1234',
        'database': 'ddareungee',
        'charset': 'utf8mb4'
    }
    
    # 예측 모델 인스턴스 생성
    predictor = BikeDemandPredictor(DB_CONFIG)
    
    # 학습용 데이터 로드
    df = predictor.load_training_data(days=30)
    
    if df is not None:
        # 학습 데이터 준비
        X, y = predictor.prepare_training_data(df)
        
        # 모델 학습
        metrics = predictor.train_model(X, y)
        print(f"학습 완료: {metrics}")
        
        # 모델 저장
        predictor.save_model('bike_demand_model.joblib')
        
        # 예측 테스트
        predictions = predictor.predict_demand('2104', hours_ahead=3)
        if predictions:
            for pred in predictions:
                print(f"{pred['predicted_time']}: {pred['predicted_bikes']}대 예상")