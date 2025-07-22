import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import mysql.connector
from datetime import datetime, timedelta
import logging
from geopy.distance import geodesic
import math
from ml_prediction import BikeDemandPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicRecommendationSystem:
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.predictor = BikeDemandPredictor(db_config)
        
    def load_predictor_model(self, model_path: str):
        """예측 모델 로드"""
        try:
            self.predictor.load_model(model_path)
            logger.info("예측 모델 로드 완료")
        except Exception as e:
            logger.error(f"예측 모델 로드 실패: {e}")
    
    def get_nearby_stations(self, lat: float, lng: float, radius_km: float = 2.0) -> List[Dict]:
        """주변 대여소 조회"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            
            query = """
            SELECT DISTINCT station_id, station_name, station_lat, station_lng,
                   park_cnt, rack_cnt, collected_at
            FROM realtime_bike_status r1
            WHERE r1.collected_at = (
                SELECT MAX(r2.collected_at) 
                FROM realtime_bike_status r2 
                WHERE r2.station_id = r1.station_id
            )
            AND r1.collected_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
            """
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            if df.empty:
                return []
            
            # 거리 계산
            nearby_stations = []
            user_location = (lat, lng)
            
            for _, station in df.iterrows():
                station_location = (station['station_lat'], station['station_lng'])
                distance = geodesic(user_location, station_location).kilometers
                
                if distance <= radius_km:
                    nearby_stations.append({
                        'station_id': station['station_id'],
                        'station_name': station['station_name'],
                        'latitude': station['station_lat'],
                        'longitude': station['station_lng'],
                        'current_bikes': station['park_cnt'],
                        'total_racks': station['rack_cnt'],
                        'distance_km': round(distance, 2),
                        'availability_rate': station['park_cnt'] / station['rack_cnt'] if station['rack_cnt'] > 0 else 0,
                        'last_updated': station['collected_at']
                    })
            
            return sorted(nearby_stations, key=lambda x: x['distance_km'])
            
        except Exception as e:
            logger.error(f"주변 대여소 조회 오류: {e}")
            return []
    
    def calculate_station_score(self, station: Dict, user_lat: float, user_lng: float, 
                              destination_lat: float = None, destination_lng: float = None,
                              purpose: str = 'rental') -> float:
        """대여소 점수 계산"""
        score = 0
        
        # 1. 가용성 점수 (40%)
        if purpose == 'rental':
            availability = station['current_bikes'] / station['total_racks']
            score += availability * 0.4
        else:  # return
            empty_spots = (station['total_racks'] - station['current_bikes']) / station['total_racks']
            score += empty_spots * 0.4
        
        # 2. 거리 점수 (30%)
        distance_score = max(0, (2.0 - station['distance_km']) / 2.0)
        score += distance_score * 0.3
        
        # 3. 목적지 접근성 점수 (20%)
        if destination_lat and destination_lng:
            station_to_dest = geodesic(
                (station['latitude'], station['longitude']),
                (destination_lat, destination_lng)
            ).kilometers
            dest_score = max(0, (3.0 - station_to_dest) / 3.0)
            score += dest_score * 0.2
        else:
            score += 0.1  # 목적지 없을 때 기본 점수
        
        # 4. 예측 점수 (10%)
        predictions = self.predictor.predict_demand(station['station_id'], hours_ahead=1)
        if predictions:
            future_availability = predictions[0]['predicted_availability']
            if purpose == 'rental':
                pred_score = future_availability
            else:
                pred_score = 1 - future_availability
            score += pred_score * 0.1
        
        return min(1.0, score)
    
    def get_recommendations(self, user_lat: float, user_lng: float, 
                          destination_lat: float = None, destination_lng: float = None,
                          purpose: str = 'rental', top_n: int = 5) -> List[Dict]:
        """동적 추천 시스템"""
        try:
            # 주변 대여소 조회
            nearby_stations = self.get_nearby_stations(user_lat, user_lng)
            
            if not nearby_stations:
                logger.warning("주변 대여소가 없습니다.")
                return []
            
            # 각 대여소 점수 계산
            recommendations = []
            
            for station in nearby_stations:
                score = self.calculate_station_score(
                    station, user_lat, user_lng, destination_lat, destination_lng, purpose
                )
                
                # 예측 정보 추가
                predictions = self.predictor.predict_demand(station['station_id'], hours_ahead=2)
                
                recommendation = {
                    'station_id': station['station_id'],
                    'station_name': station['station_name'],
                    'latitude': station['latitude'],
                    'longitude': station['longitude'],
                    'current_bikes': station['current_bikes'],
                    'total_racks': station['total_racks'],
                    'distance_km': station['distance_km'],
                    'availability_rate': station['availability_rate'],
                    'recommendation_score': round(score, 3),
                    'predicted_bikes': predictions[0]['predicted_bikes'] if predictions else station['current_bikes'],
                    'predicted_availability': predictions[0]['predicted_availability'] if predictions else station['availability_rate'],
                    'confidence': self._calculate_confidence(station, predictions),
                    'walking_time_minutes': self._calculate_walking_time(station['distance_km']),
                    'status': self._get_status(station, purpose),
                    'last_updated': station['last_updated']
                }
                
                recommendations.append(recommendation)
            
            # 점수 기준 정렬
            recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            # 상위 N개 반환
            return recommendations[:top_n]
            
        except Exception as e:
            logger.error(f"추천 시스템 오류: {e}")
            return []
    
    def _calculate_confidence(self, station: Dict, predictions: List[Dict]) -> str:
        """예측 신뢰도 계산"""
        if not predictions:
            return "low"
        
        current_bikes = station['current_bikes']
        predicted_bikes = predictions[0]['predicted_bikes']
        
        # 예측 변화량 기준 신뢰도
        change_ratio = abs(predicted_bikes - current_bikes) / station['total_racks']
        
        if change_ratio < 0.1:
            return "high"
        elif change_ratio < 0.3:
            return "medium"
        else:
            return "low"
    
    def _calculate_walking_time(self, distance_km: float) -> int:
        """도보 이동 시간 계산 (분)"""
        walking_speed_kmh = 4.0  # 평균 도보 속도 4km/h
        return int((distance_km / walking_speed_kmh) * 60)
    
    def _get_status(self, station: Dict, purpose: str) -> str:
        """대여소 상태 판단"""
        if purpose == 'rental':
            if station['current_bikes'] == 0:
                return "empty"
            elif station['current_bikes'] <= 2:
                return "low"
            elif station['current_bikes'] >= station['total_racks'] * 0.7:
                return "high"
            else:
                return "medium"
        else:  # return
            empty_spots = station['total_racks'] - station['current_bikes']
            if empty_spots == 0:
                return "full"
            elif empty_spots <= 2:
                return "low"
            elif empty_spots >= station['total_racks'] * 0.7:
                return "high"
            else:
                return "medium"
    
    def get_route_recommendations(self, start_lat: float, start_lng: float,
                                end_lat: float, end_lng: float) -> Dict:
        """경로 기반 추천"""
        try:
            # 출발지 주변 대여소 (대여용)
            departure_recommendations = self.get_recommendations(
                start_lat, start_lng, end_lat, end_lng, purpose='rental', top_n=3
            )
            
            # 도착지 주변 대여소 (반납용)
            arrival_recommendations = self.get_recommendations(
                end_lat, end_lng, start_lat, start_lng, purpose='return', top_n=3
            )
            
            # 경로 정보 계산
            total_distance = geodesic((start_lat, start_lng), (end_lat, end_lng)).kilometers
            
            return {
                'departure_stations': departure_recommendations,
                'arrival_stations': arrival_recommendations,
                'route_info': {
                    'total_distance_km': round(total_distance, 2),
                    'estimated_bike_time_minutes': int((total_distance / 15) * 60),  # 평균 자전거 속도 15km/h
                    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
        except Exception as e:
            logger.error(f"경로 추천 오류: {e}")
            return {}

if __name__ == "__main__":
    # 설정
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '1234',
        'database': 'ddareungee',
        'charset': 'utf8mb4'
    }
    
    # 추천 시스템 인스턴스 생성
    recommender = DynamicRecommendationSystem(DB_CONFIG)
    
    # 예측 모델 로드 (사전에 학습된 모델 필요)
    try:
        recommender.load_predictor_model('bike_demand_model.joblib')
    except:
        logger.warning("예측 모델을 로드할 수 없습니다. 예측 기능 없이 실행됩니다.")
    
    # 테스트 - 강남역 주변 대여소 추천
    gangnam_lat, gangnam_lng = 37.498095, 127.027610
    
    recommendations = recommender.get_recommendations(
        gangnam_lat, gangnam_lng, purpose='rental', top_n=5
    )
    
    print("=== 강남역 주변 대여소 추천 ===")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['station_name']}")
        print(f"   점수: {rec['recommendation_score']}, 거리: {rec['distance_km']}km")
        print(f"   현재 자전거: {rec['current_bikes']}대, 예상: {rec['predicted_bikes']}대")
        print(f"   상태: {rec['status']}, 신뢰도: {rec['confidence']}")
        print()
    
    # 경로 추천 테스트
    route_rec = recommender.get_route_recommendations(
        gangnam_lat, gangnam_lng, 37.521229, 126.924229  # 강남역 -> 홍대입구역
    )
    
    if route_rec:
        print("=== 경로 추천 ===")
        print(f"총 거리: {route_rec['route_info']['total_distance_km']}km")
        print(f"예상 이동 시간: {route_rec['route_info']['estimated_bike_time_minutes']}분")
        print(f"출발지 추천: {len(route_rec['departure_stations'])}개")
        print(f"도착지 추천: {len(route_rec['arrival_stations'])}개")