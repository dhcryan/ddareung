

from flask import Flask, render_template
import pandas as pd
import os
from page_renderer import PageRenderer
from bike_dataset import build_df


app = Flask(__name__)
cur_path = os.path.curdir
dataset_path = os.path.join(cur_path, 'Dataset')

@app.route('/')
def map():
    df, rental_df = build_df('seoul_bike_2022.csv')
    #renderer = PageRenderer()
    return render_template('seongdong_df.html')


if __name__ == '__main__':
    # 데이터셋 렌더링

    app.run()
