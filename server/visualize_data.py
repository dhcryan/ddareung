import sqlite3
import pandas as pd
import folium
from folium.plugins import HeatMap
import webbrowser
import os

def create_bike_map():
    """실시간 따릉이 현황 지도 생성"""
    # 데이터베이스 연결
    conn = sqlite3.connect('ddareung.db')
    
    # 최신 데이터 조회
    query = """
    SELECT station_id, station_name, park_cnt, rack_cnt, 
           station_lat, station_lng, collected_at
    FROM realtime_bike_status 
    WHERE collected_at = (SELECT MAX(collected_at) FROM realtime_bike_status)
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"총 {len(df)}개 대여소 데이터 로드")
    
    # 지도 생성 (서울 중심)
    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # 대여소별 마커 추가
    for _, station in df.iterrows():
        # 자전거 수량에 따른 색상 결정
        if station['park_cnt'] == 0:
            color = 'red'
            icon = 'remove'
        elif station['park_cnt'] <= 2:
            color = 'orange'
            icon = 'exclamation-sign'
        elif station['park_cnt'] >= station['rack_cnt'] * 0.8:
            color = 'green'
            icon = 'ok-sign'
        else:
            color = 'blue'
            icon = 'info-sign'
        
        # 팝업 정보
        popup_text = f"""
        <b>{station['station_name']}</b><br>
        자전거: {station['park_cnt']}대<br>
        총 거치대: {station['rack_cnt']}대<br>
        이용률: {station['park_cnt']/station['rack_cnt']*100:.1f}%<br>
        업데이트: {station['collected_at']}
        """
        
        folium.Marker(
            location=[station['station_lat'], station['station_lng']],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"{station['station_name']}: {station['park_cnt']}대",
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(m)
    
    # 히트맵 레이어 추가
    heat_data = []
    for _, station in df.iterrows():
        if station['park_cnt'] > 0:
            heat_data.append([
                station['station_lat'], 
                station['station_lng'], 
                station['park_cnt']
            ])
    
    if heat_data:
        HeatMap(heat_data, radius=15, blur=10).add_to(m)
    
    # 범례 추가
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>따릉이 현황</h4>
    <i class="fa fa-circle" style="color:red"></i> 자전거 없음 (0대)<br>
    <i class="fa fa-circle" style="color:orange"></i> 부족 (1-2대)<br>
    <i class="fa fa-circle" style="color:blue"></i> 보통<br>
    <i class="fa fa-circle" style="color:green"></i> 충분 (80% 이상)<br>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # 지도 저장
    map_path = 'bike_status_map.html'
    m.save(map_path)
    
    print(f"지도 생성 완료: {map_path}")
    print(f"브라우저에서 확인: file://{os.path.abspath(map_path)}")
    
    return map_path

def show_statistics():
    """현재 따릉이 현황 통계"""
    conn = sqlite3.connect('ddareung.db')
    
    # 통계 쿼리
    stats_query = """
    SELECT 
        COUNT(*) as total_stations,
        SUM(park_cnt) as total_bikes,
        SUM(rack_cnt) as total_racks,
        AVG(park_cnt) as avg_bikes_per_station,
        SUM(CASE WHEN park_cnt = 0 THEN 1 ELSE 0 END) as empty_stations,
        SUM(CASE WHEN park_cnt <= 2 THEN 1 ELSE 0 END) as low_stations,
        SUM(CASE WHEN park_cnt >= rack_cnt * 0.8 THEN 1 ELSE 0 END) as full_stations
    FROM realtime_bike_status 
    WHERE collected_at = (SELECT MAX(collected_at) FROM realtime_bike_status)
    """
    
    stats = pd.read_sql_query(stats_query, conn)
    conn.close()
    
    print("=== 서울시 따릉이 현황 통계 ===")
    print(f"총 대여소: {stats['total_stations'].iloc[0]:,}개")
    print(f"총 자전거: {stats['total_bikes'].iloc[0]:,}대")
    print(f"총 거치대: {stats['total_racks'].iloc[0]:,}개")
    print(f"대여소당 평균 자전거: {stats['avg_bikes_per_station'].iloc[0]:.1f}대")
    print(f"자전거 없는 대여소: {stats['empty_stations'].iloc[0]:,}개")
    print(f"자전거 부족 대여소: {stats['low_stations'].iloc[0]:,}개")
    print(f"자전거 충분한 대여소: {stats['full_stations'].iloc[0]:,}개")
    
    utilization = stats['total_bikes'].iloc[0] / stats['total_racks'].iloc[0] * 100
    print(f"전체 이용률: {utilization:.1f}%")

if __name__ == "__main__":
    print("따릉이 실시간 현황 분석 시작...")
    
    # 통계 출력
    show_statistics()
    
    print("\n지도 생성 중...")
    # 지도 생성
    map_path = create_bike_map()
    
    print(f"\n결과 확인 방법:")
    print(f"1. 웹브라우저에서 file://{os.path.abspath(map_path)} 열기")
    print(f"2. 또는 다음 명령어 실행:")
    print(f"   open {map_path}  # macOS")
    print(f"   xdg-open {map_path}  # Linux")