import requests
import json
import time
import pandas as pd
import mysql.connector
from datetime import datetime
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeoulBikeAPI:
    def __init__(self, api_key: str, db_config: Dict):
        self.api_key = api_key
        self.db_config = db_config
        self.base_url = "http://openapi.seoul.go.kr:8088"
        
    def get_realtime_station_info(self) -> Optional[List[Dict]]:
        """서울시 공공자전거 실시간 대여정보 조회"""
        try:
            url = f"{self.base_url}/{self.api_key}/json/bikeList/1/1000/"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'bikeList' not in data:
                logger.error("API 응답에 bikeList가 없습니다.")
                return None
                
            stations = data['bikeList']['row']
            logger.info(f"수집된 대여소 수: {len(stations)}")
            return stations
            
        except requests.RequestException as e:
            logger.error(f"API 요청 실패: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            return None
    
    def save_to_database(self, stations: List[Dict]) -> bool:
        """실시간 데이터를 데이터베이스에 저장"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 실시간 데이터 테이블 생성
            create_table_query = """
            CREATE TABLE IF NOT EXISTS realtime_bike_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                station_id VARCHAR(10) NOT NULL,
                station_name VARCHAR(100) NOT NULL,
                park_cnt INT NOT NULL,
                rack_cnt INT NOT NULL,
                shared INT NOT NULL,
                station_lat DECIMAL(10, 8),
                station_lng DECIMAL(11, 8),
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_station_time (station_id, collected_at),
                INDEX idx_collected_at (collected_at)
            )
            """
            cursor.execute(create_table_query)
            
            # 데이터 삽입
            insert_query = """
            INSERT INTO realtime_bike_status 
            (station_id, station_name, park_cnt, rack_cnt, shared, station_lat, station_lng)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            for station in stations:
                values = (
                    station.get('stationId', ''),
                    station.get('stationName', ''),
                    int(station.get('parkingBikeTotCnt', 0)),
                    int(station.get('rackTotCnt', 0)),
                    int(station.get('shared', 0)),
                    float(station.get('stationLatitude', 0)),
                    float(station.get('stationLongitude', 0))
                )
                cursor.execute(insert_query, values)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"데이터베이스에 {len(stations)}개 대여소 정보 저장 완료")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"데이터베이스 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"데이터 저장 중 오류: {e}")
            return False
    
    def get_station_trend(self, station_id: str, hours: int = 24) -> Optional[pd.DataFrame]:
        """특정 대여소의 시간별 변화 추이 조회"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            
            query = """
            SELECT station_id, station_name, park_cnt, rack_cnt, collected_at
            FROM realtime_bike_status 
            WHERE station_id = %s 
            AND collected_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
            ORDER BY collected_at DESC
            """
            
            df = pd.read_sql(query, conn, params=(station_id, hours))
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"추이 데이터 조회 오류: {e}")
            return None
    
    def collect_data_continuously(self, interval_minutes: int = 10):
        """지속적인 데이터 수집"""
        logger.info(f"실시간 데이터 수집 시작 (수집 간격: {interval_minutes}분)")
        
        while True:
            try:
                stations = self.get_realtime_station_info()
                if stations:
                    self.save_to_database(stations)
                    logger.info(f"데이터 수집 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    logger.warning("데이터 수집 실패")
                
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("데이터 수집 중단")
                break
            except Exception as e:
                logger.error(f"데이터 수집 중 오류: {e}")
                time.sleep(60)  # 1분 후 재시도

if __name__ == "__main__":
    # 설정
    API_KEY = "YOUR_API_KEY_HERE"  # 실제 API 키로 교체 필요
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '1234',
        'database': 'ddareungee',
        'charset': 'utf8mb4'
    }
    
    # API 클래스 인스턴스 생성
    api = SeoulBikeAPI(API_KEY, DB_CONFIG)
    
    # 실시간 데이터 수집 시작
    api.collect_data_continuously(interval_minutes=10)