
from flask import Flask, render_template, request     
import test 

app = Flask(__name__)              

@app.route('/')                     # 라우팅 설정
def index():                  # 함수 정의
    # get 을 통한 전달받은 데이터를 확인
    key1 = request.args.get('keyword1')
    key2 = request.args.get('keyword2')
    print(type(key1), type(key2))

    if key1 == "" or key2 == "":
        return render_template('index.html')
    else:
        value1 = test.print_test(key1)
        value2 = test.print_test(key2)

        data = { 'key1': value1, 'key2': value2}
        return render_template('index.html', data=data)

if __name__ == '__main__':          # 메인 함수
    app.run(debug=True)                       # 실행

# Path: templates/index.html


