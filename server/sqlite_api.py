import requests
import json
import time
import pandas as pd
import sqlite3
from datetime import datetime
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeoulBikeAPI:
    def __init__(self, api_key: str, db_path: str):
        self.api_key = api_key
        self.db_path = db_path
        self.base_url = "http://openapi.seoul.go.kr:8088"
        self.init_database()
        
    def init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 실시간 데이터 테이블 생성
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_bike_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id TEXT NOT NULL,
                station_name TEXT NOT NULL,
                park_cnt INTEGER NOT NULL,
                rack_cnt INTEGER NOT NULL,
                shared INTEGER NOT NULL,
                station_lat REAL,
                station_lng REAL,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_station_time ON realtime_bike_status(station_id, collected_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_collected_at ON realtime_bike_status(collected_at)')
            
            conn.commit()
            conn.close()
            logger.info("데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
    
    def get_realtime_station_info(self) -> Optional[List[Dict]]:
        """서울시 공공자전거 실시간 대여정보 조회"""
        try:
            url = f"{self.base_url}/{self.api_key}/json/bikeList/1/1000/"
            logger.info(f"API 요청 URL: {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            # logger.info(f"API 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if 'rentBikeStatus' not in data:
                logger.error("API 응답에 rentBikeStatus가 없습니다.")
                # 다른 키 구조 확인
                logger.info(f"응답 키 목록: {list(data.keys())}")
                return None
                
            stations = data['rentBikeStatus']['row']
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 데이터 삽입
            for station in stations:
                cursor.execute('''
                INSERT INTO realtime_bike_status 
                (station_id, station_name, park_cnt, rack_cnt, shared, station_lat, station_lng)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    station.get('stationId', ''),
                    station.get('stationName', ''),
                    int(station.get('parkingBikeTotCnt', 0)),
                    int(station.get('rackTotCnt', 0)),
                    int(station.get('shared', 0)),
                    float(station.get('stationLatitude', 0)),
                    float(station.get('stationLongitude', 0))
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"데이터베이스에 {len(stations)}개 대여소 정보 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"데이터 저장 중 오류: {e}")
            return False
    
    def get_station_trend(self, station_id: str, hours: int = 24) -> Optional[pd.DataFrame]:
        """특정 대여소의 시간별 변화 추이 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
            SELECT station_id, station_name, park_cnt, rack_cnt, collected_at
            FROM realtime_bike_status 
            WHERE station_id = ?
            AND collected_at >= datetime('now', '-{} hours')
            ORDER BY collected_at DESC
            '''.format(hours)
            
            df = pd.read_sql_query(query, conn, params=(station_id,))
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"추이 데이터 조회 오류: {e}")
            return None

if __name__ == "__main__":
    # 테스트
    from config import Config
    
    api = SeoulBikeAPI(Config.SEOUL_API_KEY, "ddareung.db")
    
    # 실시간 데이터 수집 테스트
    stations = api.get_realtime_station_info()
    if stations:
        api.save_to_database(stations)
        print("데이터 수집 및 저장 완료!")
    else:
        print("데이터 수집 실패")