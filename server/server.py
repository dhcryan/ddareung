

from flask import Flask, render_template, request, jsonify
from flask.json import JSONEncoder
import pandas as pd
import os
from page_renderer import PageRenderer
from bike_dataset import build_df
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="1234",
    database="ddareungee"
)

mc = mydb.cursor()
app = Flask(__name__)
cur_path = os.path.curdir
dataset_path = os.path.join(cur_path, 'Dataset')

## 시간 오래 걸림

@app.route('/', methods=['GET'])
def map():

    # 사용자로부터 입력받을 parameters
    depart = '2266'
    #depart = request.args.get('depart')
    dest = '103'
    #dest = request.args.get('dest')
    search_time = '2022-06-01 18:42:30'
    #initial_time = request.args.get('initial_time')
    initial_time = search_time[:-8]+'00:00:00'

    mc.execute(f"SELECT 자치구 FROM rental_spot WHERE 대여소번호 = {depart}".format(depart=depart))
    depart_gu = mc.fetchone()[0]
    mc.execute(f"SELECT 자치구 FROM rental_spot WHERE 대여소번호 = {dest}".format(dest=dest))
    dest_gu = mc.fetchone()[0]
    print(depart_gu, dest_gu)

    # 출발지 자치구
    mc.execute(f"SELECT * FROM rental_spot WHERE 자치구 = '{depart_gu}'".format(depart_gu=depart_gu))
    depart_spots = pd.DataFrame(mc.fetchall())
    depart_spots.columns = ['대여소번호', '보관소(대여소)명', '자치구', '상세주소', '위도', '경도', 'LCD', 'QR', '거치대개수']

    # 목적지 자치구
    mc.execute(f"SELECT * FROM rental_spot WHERE 자치구 = '{dest_gu}'".format(dest_gu=dest_gu))
    dest_spots = pd.DataFrame(mc.fetchall())
    dest_spots.columns = ['대여소번호', '보관소(대여소)명', '자치구', '상세주소', '위도', '경도', 'LCD', 'QR', '거치대개수']

    #depart_spot_list = '('+str(depart_spots['대여소번호'].tolist())[1:-1]+')'  # 추후 주변 3~4개 정도의 대여소로 줄일 예정
    depart_spot_list = depart_spots['대여소번호'].tolist()
    #dest_spot_list = '('+str(dest_spots['대여소번호'].tolist())[1:-1]+')' # 추후 주변 3~4개 정도의 대여소로 줄일 예정
    dest_spot_list = dest_spots['대여소번호'].tolist()
    concat_list = '('+str(list(set(depart_spot_list+dest_spot_list)))[1:-1]+')'

    # 0시부터 search_time까지의 대여 리스트
    mc.execute(f"SELECT 대여대여소, count(*)\
                FROM bike_log\
                WHERE 대여일시 > '{initial_time}' AND 대여일시 < '{search_time}' AND 대여대여소 IN {concat_list}\
                GROUP BY 대여대여소;\
                ".format(initial_time=initial_time, search_time=search_time, concat_list=concat_list))
    rental_list = pd.DataFrame((mc.fetchall()))
    rental_list.columns=['대여소번호', '대여량']
    print(rental_list)

    # 0시부터 search_time까지의 반납 리스트
    mc.execute(f"SELECT 반납대여소, count(*)\
                FROM bike_log\
                WHERE 반납일시 > '{initial_time}' AND 반납일시 < '{search_time}' AND 반납대여소 IN {concat_list}\
                GROUP BY 반납대여소;\
                ".format(initial_time=initial_time, search_time=search_time, concat_list=concat_list))
    return_list = pd.DataFrame(mc.fetchall())
    return_list.columns=['대여소번호', '반납량']
    print(return_list)

    # 출발지,목적지 인근 각 대여소별 대여/반납 리스트
    total_list = pd.merge(depart_spots[['대여소번호', '보관소(대여소)명', '자치구', '상세주소', '위도', '경도', '거치대개수']],
                        dest_spots[['대여소번호', '보관소(대여소)명', '자치구', '상세주소', '위도', '경도', '거치대개수']], 
                        on=['대여소번호', '보관소(대여소)명', '자치구', '상세주소', '위도', '경도', '거치대개수'], how='outer')

    total_list = pd.merge(total_list, rental_list, how='left', on='대여소번호')
    total_list = pd.merge(total_list, return_list, how='left', on='대여소번호')

    print(total_list)

    total_list['자전거대수'] = total_list['거치대개수']-total_list['대여량']+total_list['반납량']
    total_list.drop(axis=1, labels=['거치대개수', '대여량', '반납량'], inplace=True)

    total_list.loc[(total_list['자전거대수'] < 0), '자전거대수'] = 0. # 자전거 부족할 경우 모두 0
    total_list.fillna(0, inplace=True) #NaN값 제거

    print(total_list)

    # 출발지/목적지로 분할
    departure = total_list.loc[total_list['대여소번호']==int(depart)]
    destination = total_list.loc[total_list['대여소번호']==int(dest)]
    depart_group = pd.merge(depart_spots.drop(columns=['QR', 'LCD', '거치대개수']), total_list[['대여소번호', '자전거대수']], how='left', on='대여소번호')
    depart_group = depart_group.loc[depart_group['대여소번호']!=int(depart)]
    dest_group = pd.merge(dest_spots.drop(columns=['QR', 'LCD', '거치대개수']), total_list[['대여소번호', '자전거대수']], how='left', on='대여소번호')
    dest_group = dest_group.loc[dest_group['대여소번호']!=int(dest)]

    print("======================")
    print(departure)
    print("======================")
    print(destination)
    print("======================")
    print(depart_group)
    print("======================")
    print(dest_group)
    print("======================")
    
    result = {
        "departure": departure.to_json(),
        "departure_group": depart_group.to_json(),
        "destination": destination.to_json(),
        "destination_group": dest_group.to_json()
    }

    print(result)
    
    return jsonify({
        'result': result
    })


if __name__ == '__main__':
    # 데이터셋 렌더링
    app.run()
