from pyproj import Transformer
import pyproj
from shapely.geometry import Point as point
import geopandas as gpd
import folium
from collections import namedtuple
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import geodesic
from plotnine import *
from scipy import stats
from folium.plugins import MarkerCluster
import json


font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')
[fm.FontProperties(fname=font).get_name() for font in font_list]

plt.rcParams["font.family"] = 'NanumGothic'


class PageRenderer:
    def __init__(self, depart, dest, time, rental) -> None:
        self.myMap = folium.Map[lat, long], zoom_start=10
        coords = []
        for i in range(len(rental_df)-1):
            x = rental_df['위도'][i]
            y = rental_df['경도'][i]
            coords.append([x, y])
            
        for i in range(len(coords)):
            folium.Circle(
                location = coords[i],
                radius = 100,
                color = 'RdYlGn',
                fill = 'crimson',
            ).add_to(self.myMap)
        

    def plot(self, df):
        # 리스트를 이용해 여러 행의 데이터를 위,경도로 묶음
        locations = list(zip(df.위도, df.경도))
        # 반복문을 이용해 locations로 정의한 변수에 해당하는 위치에 자동차 모양의 빨간색 아이콘을 지정했다.
        icons = [folium.Icon(icon='fa-bicycle', prefix="fa", color="blue") for _ in range(len(locations))]

        # 역시 같은 원리로 아이콘을 클릭했을 때, 팝업이 생성되게 할 예정인데, 먼저 팝업 안에 들어갈 내용을 지정한다.
        popup_content = []
        for information in df.itertuples():
            content = "<b>대여소번호 : {}</b>  <br /> 대여소명: {}".format(information.대여소번호, information._2)
            popup_content.append(content)
        popups = [folium.Popup(content, min_width=300, max_width=300) for content in popup_content]
        cluster = MarkerCluster(locations = locations, icons = icons, popups = popups)
        # 지도에 클러스터를 추가.
        cluster.add_to(self.myMap)

if __name__ == "__main__":
    # print(fm.findSystemFonts(fontpaths=None, fontext='ttf'))
    print ('버전: ', mpl.__version__)
    print ('설치 위치: ', mpl.__file__)
    print ('설정 위치: ', mpl.get_configdir())
    print ('캐시 위치: ', mpl.get_cachedir())

df_2022=pd.read_csv(low_memory=False)