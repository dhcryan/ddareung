
from flask import Flask, render_template, request     
from flask_cors import CORS
import test 

app = Flask(__name__)     
CORS(app,
    resources={
        r"/*": { "origins": "http://localhost:3000" }},
    supports_credentials=True
    )         

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

@app.route('/users')
def users():
	# users 데이터를 Json 형식으로 반환한다
    return {"members": [{ "id" : 1, "name" : "yerin" },
    					{ "id" : 2, "name" : "dalkong" }]}

@app.route("/search", methods=["POST"])
def postStationData():
    # POST 요청을 받아서 처리한다
    data = request.get_json()
    print(data)
    return data 


if __name__ == '__main__':          # 메인 함수
    app.run(debug=True)                       # 실행

# Path: templates/index.html


