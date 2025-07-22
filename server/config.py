import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 데이터베이스 설정
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '1234'),
        'database': os.getenv('DB_NAME', 'ddareungee'),
        'charset': 'utf8mb4'
    }
    
    # API 설정
    SEOUL_API_KEY = os.getenv('SEOUL_API_KEY', 'YOUR_API_KEY_HERE')
    
    # Redis 설정
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = os.getenv('REDIS_PORT', 6379)
    REDIS_DB = os.getenv('REDIS_DB', 0)
    
    # 캐시 설정
    CACHE_TIMEOUT = 300  # 5분
    
    # 예측 모델 설정
    MODEL_PATH = os.getenv('MODEL_PATH', 'bike_demand_model.joblib')
    MODEL_RETRAIN_HOURS = int(os.getenv('MODEL_RETRAIN_HOURS', 24))
    
    # 데이터 수집 설정
    DATA_COLLECTION_INTERVAL = int(os.getenv('DATA_COLLECTION_INTERVAL', 10))  # 분
    
    # 추천 시스템 설정
    DEFAULT_SEARCH_RADIUS = float(os.getenv('DEFAULT_SEARCH_RADIUS', 2.0))  # km
    MAX_RECOMMENDATIONS = int(os.getenv('MAX_RECOMMENDATIONS', 10))
    
    # 로깅 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
class TestingConfig(Config):
    TESTING = True
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'test',
        'password': 'test',
        'database': 'test_ddareungee',
        'charset': 'utf8mb4'
    }

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}