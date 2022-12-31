import os
import pandas as pd

dataset_path = os.path.join(os.path.curdir, 'Dataset')

def build_df(file_name):
    # 데이터셋 빌드
    df=pd.read_csv(os.path.join(dataset_path, file_name), low_memory=False)

    # 유효한 대여소 번호 구간 정하기
    df=df[(df.loc[:,'대여대여소']>=102) & (df.loc[:,'대여대여소']<=5855) & (df.loc[:,'반납대여소']>=102) & (df.loc[:,'반납대여소']<=5855)]
    df["대여연월"] = df["대여일시"].apply(lambda x : x[:7])
    df["대여일시"]=pd.to_datetime(df["대여일시"])

    df["대여연도"] = df["대여일시"].dt.year
    df["대여월"] = df["대여일시"].dt.month
    df["대여일"] = df["대여일시"].dt.day
    df["대여시간"] = df["대여일시"].dt.hour
    df["대여요일"] = df["대여일시"].dt.dayofweek
    df["대여일자"] = df["대여일시"].dt.date

    df["반납연월"] = df["반납일시"].apply(lambda x : x[:7])
    df["반납일시"]=pd.to_datetime(df["반납일시"])

    df["반납일시"]=pd.to_datetime(df["반납일시"])
    df["반납연도"] = df["반납일시"].dt.year
    df["반납월"] = df["반납일시"].dt.month
    df["반납일"] = df["반납일시"].dt.day
    df["반납시간"] = df["반납일시"].dt.hour
    df["반납요일"] = df["반납일시"].dt.dayofweek
    df["반납일자"] = df["반납일시"].dt.date

    ### 거치소 dataframe
    rental_df=pd.read_csv(os.path.join(dataset_path, 'rental_spot.csv'), low_memory=False, encoding='cp949')
    del rental_df['LCD']
    del rental_df['QR']
    # rental_df_gu: 대여한 대여소번호의 자치구
    rental_df_gu=rental_df[['대여소번호','자치구']]
    rental_df_gu.columns=['대여대여소','대여지역']
    # return_df_gu: 반납한 반납소번호의 자치구
    return_df_gu=rental_df[['대여소번호','자치구']]
    return_df_gu.columns=['반납대여소','반납지역']

    ### 2022 dataframe과 대여소번호, 반납소번호를 key로 삼아 자치구만 추가해주기(대여지역, 반납 지역 다 있음)
    df=pd.merge(left = df , right = rental_df_gu, how = "inner", on = "대여대여소")
    df=pd.merge(left = df , right = return_df_gu, how = "inner", on = "반납대여소")

    return df, rental_df