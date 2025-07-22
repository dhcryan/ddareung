from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime
from real_time_api import SeoulBikeAPI
from ml_prediction import BikeDemandPredictor
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.bike_api = SeoulBikeAPI(Config.SEOUL_API_KEY, Config.DB_CONFIG)
        self.predictor = BikeDemandPredictor(Config.DB_CONFIG)
        
    def start(self):
        """스케줄러 시작"""
        # 실시간 데이터 수집 작업
        self.scheduler.add_job(
            func=self.collect_realtime_data,
            trigger=IntervalTrigger(minutes=Config.DATA_COLLECTION_INTERVAL),
            id='data_collection',
            name='실시간 데이터 수집',
            replace_existing=True
        )
        
        # 모델 재학습 작업
        self.scheduler.add_job(
            func=self.retrain_model,
            trigger=IntervalTrigger(hours=Config.MODEL_RETRAIN_HOURS),
            id='model_retraining',
            name='모델 재학습',
            replace_existing=True
        )
        
        # 데이터 정리 작업 (매일 자정)
        self.scheduler.add_job(
            func=self.cleanup_old_data,
            trigger='cron',
            hour=0,
            minute=0,
            id='data_cleanup',
            name='오래된 데이터 정리',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("스케줄러 시작 완료")
        
    def stop(self):
        """스케줄러 중지"""
        self.scheduler.shutdown()
        logger.info("스케줄러 중지 완료")
        
    def collect_realtime_data(self):
        """실시간 데이터 수집 작업"""
        try:
            logger.info("실시간 데이터 수집 시작")
            stations = self.bike_api.get_realtime_station_info()
            
            if stations:
                success = self.bike_api.save_to_database(stations)
                if success:
                    logger.info(f"실시간 데이터 수집 완료: {len(stations)}개 대여소")
                else:
                    logger.error("데이터 저장 실패")
            else:
                logger.warning("실시간 데이터 가져오기 실패")
                
        except Exception as e:
            logger.error(f"실시간 데이터 수집 오류: {e}")
            
    def retrain_model(self):
        """모델 재학습 작업"""
        try:
            logger.info("모델 재학습 시작")
            
            # 학습용 데이터 로드
            df = self.predictor.load_training_data(days=30)
            
            if df is not None:
                # 학습 데이터 준비
                X, y = self.predictor.prepare_training_data(df)
                
                # 모델 학습
                metrics = self.predictor.train_model(X, y)
                
                # 모델 저장
                self.predictor.save_model(Config.MODEL_PATH)
                
                logger.info(f"모델 재학습 완료: {metrics}")
            else:
                logger.warning("학습용 데이터가 없습니다.")
                
        except Exception as e:
            logger.error(f"모델 재학습 오류: {e}")
            
    def cleanup_old_data(self):
        """오래된 데이터 정리 작업"""
        try:
            import mysql.connector
            
            logger.info("오래된 데이터 정리 시작")
            
            conn = mysql.connector.connect(**Config.DB_CONFIG)
            cursor = conn.cursor()
            
            # 30일 이전 데이터 삭제
            cleanup_query = """
            DELETE FROM realtime_bike_status 
            WHERE collected_at < DATE_SUB(NOW(), INTERVAL 30 DAY)
            """
            
            cursor.execute(cleanup_query)
            deleted_rows = cursor.rowcount
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"오래된 데이터 정리 완료: {deleted_rows}개 레코드 삭제")
            
        except Exception as e:
            logger.error(f"데이터 정리 오류: {e}")

if __name__ == "__main__":
    scheduler = TaskScheduler()
    scheduler.start()
    
    try:
        # 스케줄러 실행 유지
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("스케줄러 종료 요청")
        scheduler.stop()