import os
import pandas as pd

df_2018=pd.read_csv('data/seoul_bike_2018.csv',low_memory=False)
print(df_2018.describe().transpose())