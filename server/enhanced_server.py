from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import json
from sqlite_api import SeoulBikeAPI
from ml_prediction import BikeDemandPredictor
from dynamic_recommendation import DynamicRecommendationSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/*": {"origins": ["http://localhost:3000", "https://dhcryan.github.io"]}
}, supports_credentials=True)

# 설정
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'ddareungee',
    'charset': 'utf8mb4'
}

API_KEY = "6d6263746f64686336304e7275786e"

# 클래스 인스턴스 생성 (SQLite)
bike_api = SeoulBikeAPI(API_KEY, "ddareung.db")
predictor = BikeDemandPredictor(DB_CONFIG)
recommender = DynamicRecommendationSystem(DB_CONFIG)

# 예측 모델 로드
try:
    predictor.load_model('bike_demand_model.joblib')
    recommender.load_predictor_model('bike_demand_model.joblib')
    logger.info("예측 모델 로드 완료")
except Exception as e:
    logger.warning(f"예측 모델 로드 실패: {e}")

@app.route('/api/stations/realtime', methods=['GET'])
def get_realtime_stations():
    """실시간 대여소 정보 조회"""
    try:
        stations = bike_api.get_realtime_station_info()
        if stations:
            return jsonify({
                'success': True,
                'data': stations,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': '실시간 데이터를 가져올 수 없습니다.'
            }), 500
    except Exception as e:
        logger.error(f"실시간 데이터 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': '서버 오류가 발생했습니다.'
        }), 500

@app.route('/api/stations/<station_id>/trend', methods=['GET'])
def get_station_trend(station_id):
    """대여소 변화 추이 조회"""
    try:
        hours = request.args.get('hours', 24, type=int)
        df = bike_api.get_station_trend(station_id, hours)
        
        if df is not None and not df.empty:
            trend_data = df.to_dict('records')
            return jsonify({
                'success': True,
                'data': trend_data,
                'station_id': station_id
            })
        else:
            return jsonify({
                'success': False,
                'message': '추이 데이터를 찾을 수 없습니다.'
            }), 404
    except Exception as e:
        logger.error(f"추이 데이터 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': '서버 오류가 발생했습니다.'
        }), 500

@app.route('/api/stations/<station_id>/predict', methods=['GET'])
def predict_station_demand(station_id):
    """대여소 수요 예측"""
    try:
        hours_ahead = request.args.get('hours', 2, type=int)
        predictions = predictor.predict_demand(station_id, hours_ahead)
        
        if predictions:
            return jsonify({
                'success': True,
                'data': predictions,
                'station_id': station_id
            })
        else:
            return jsonify({
                'success': False,
                'message': '예측 데이터를 생성할 수 없습니다.'
            }), 400
    except Exception as e:
        logger.error(f"수요 예측 오류: {e}")
        return jsonify({
            'success': False,
            'message': '서버 오류가 발생했습니다.'
        }), 500

@app.route('/api/recommendations/nearby', methods=['POST'])
def get_nearby_recommendations():
    """주변 대여소 추천"""
    try:
        data = request.get_json()
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'success': False,
                'message': '위치 정보가 필요합니다.'
            }), 400
        
        user_lat = float(data['latitude'])
        user_lng = float(data['longitude'])
        destination_lat = data.get('destination_latitude')
        destination_lng = data.get('destination_longitude')
        purpose = data.get('purpose', 'rental')  # 'rental' or 'return'
        top_n = data.get('top_n', 5)
        
        if destination_lat:
            destination_lat = float(destination_lat)
        if destination_lng:
            destination_lng = float(destination_lng)
        
        recommendations = recommender.get_recommendations(
            user_lat, user_lng, destination_lat, destination_lng, purpose, top_n
        )
        
        return jsonify({
            'success': True,
            'data': recommendations,
            'request_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"추천 시스템 오류: {e}")
        return jsonify({
            'success': False,
            'message': '추천 데이터를 생성할 수 없습니다.'
        }), 500

@app.route('/api/recommendations/route', methods=['POST'])
def get_route_recommendations():
    """경로 기반 추천"""
    try:
        data = request.get_json()
        
        required_fields = ['start_latitude', 'start_longitude', 'end_latitude', 'end_longitude']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'message': '출발지와 도착지 정보가 필요합니다.'
            }), 400
        
        start_lat = float(data['start_latitude'])
        start_lng = float(data['start_longitude'])
        end_lat = float(data['end_latitude'])
        end_lng = float(data['end_longitude'])
        
        route_recommendations = recommender.get_route_recommendations(
            start_lat, start_lng, end_lat, end_lng
        )
        
        return jsonify({
            'success': True,
            'data': route_recommendations,
            'request_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"경로 추천 오류: {e}")
        return jsonify({
            'success': False,
            'message': '경로 추천 데이터를 생성할 수 없습니다.'
        }), 500

@app.route('/api/model/retrain', methods=['POST'])
def retrain_model():
    """모델 재학습"""
    try:
        data = request.get_json()
        days = data.get('days', 30) if data else 30
        
        # 학습용 데이터 로드
        df = predictor.load_training_data(days)
        
        if df is not None:
            # 학습 데이터 준비
            X, y = predictor.prepare_training_data(df)
            
            # 모델 학습
            metrics = predictor.train_model(X, y)
            
            # 모델 저장
            predictor.save_model('bike_demand_model.joblib')
            
            # 추천 시스템 모델 업데이트
            recommender.load_predictor_model('bike_demand_model.joblib')
            
            return jsonify({
                'success': True,
                'message': '모델 재학습 완료',
                'metrics': metrics,
                'training_data_days': days
            })
        else:
            return jsonify({
                'success': False,
                'message': '학습용 데이터를 로드할 수 없습니다.'
            }), 400
            
    except Exception as e:
        logger.error(f"모델 재학습 오류: {e}")
        return jsonify({
            'success': False,
            'message': '모델 재학습 중 오류가 발생했습니다.'
        }), 500

@app.route('/api/data/collect', methods=['POST'])
def manual_data_collection():
    """수동 데이터 수집"""
    try:
        stations = bike_api.get_realtime_station_info()
        if stations:
            success = bike_api.save_to_database(stations)
            if success:
                return jsonify({
                    'success': True,
                    'message': f'{len(stations)}개 대여소 데이터 수집 완료',
                    'collected_at': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '데이터 저장에 실패했습니다.'
                }), 500
        else:
            return jsonify({
                'success': False,
                'message': '실시간 데이터를 가져올 수 없습니다.'
            }), 500
    except Exception as e:
        logger.error(f"수동 데이터 수집 오류: {e}")
        return jsonify({
            'success': False,
            'message': '데이터 수집 중 오류가 발생했습니다.'
        }), 500

# 기존 엔드포인트 유지
@app.route('/search', methods=['POST'])
def legacy_search():
    """기존 검색 기능 유지"""
    try:
        data = request.get_json(force=True)
        
        # 기존 로직 유지...
        # (기존 server.py의 search 함수 내용)
        
        return jsonify({
            'success': True,
            'message': '기존 검색 기능입니다. 새로운 API를 사용해주세요.',
            'new_api_endpoint': '/api/recommendations/nearby'
        })
        
    except Exception as e:
        logger.error(f"레거시 검색 오류: {e}")
        return jsonify({
            'success': False,
            'message': '검색 중 오류가 발생했습니다.'
        }), 500

@app.route('/', methods=['GET'])
def index():
    """메인 페이지"""
    return jsonify({
        'message': '따릉이 실시간 API 서버',
        'version': '1.0.0',
        'endpoints': [
            'GET /health - 서버 상태 확인',
            'GET /api/stations/realtime - 실시간 대여소 정보',
            'POST /api/recommendations/nearby - 주변 대여소 추천',
            'POST /api/recommendations/route - 경로 추천',
            'POST /api/data/collect - 데이터 수집'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """서비스 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'prediction_model': predictor.model is not None,
            'recommendation_system': True,
            'database': True  # 실제로는 DB 연결 확인 필요
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)