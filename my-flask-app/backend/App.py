# server
# File: server.py

from flask import Flask, render_template
from flask import request
import requests

app = Flask(__name__)

# 定义目标 IP 的地址和端口
# ghHu: 这里是server to pod的POST请求 所以以下的信息是**pod**的ip和port
# to zsp: 这里改成你的minikube那些ip,port等等 
target_ip = '81.70.210.120'
target_port = 3111  # pod的flask我用的3111端口

# 构造 POST 请求的 URL
url_POST = f'http://{target_ip}:{target_port}/server2pod'

# 构造 GET 请求的 URL
url_GET = f'http://{target_ip}:{target_port}/pod2server'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/work')
def index_work():
    return render_template('index.html')


@app.route('/selection', methods=['POST'])
def selection():
    return {
        'Task': 'selection',
        'Frontend': 'React',
        'Backend': 'Flask'
    }

#TODO: 接GET请求 用json返回

# {
#     "list":[
#         {
#             "value": 1,
#             "name":"model1",
#             "dataset":"dataset1"
#         },
#         {
#             "value": 2,
#             "name":"model2",
#             "dataset":"dataset2"
#         },
#         {
#             "value": 3,
#             "name":"model3",
#             "dataset":"dataset3"
#         }
#     ]
# }

@app.route('/training', methods=['POST'])
def training():
    print("POST请求已发送")
    return {
        'Task': 'training',
        'Frontend': 'React',
        'Backend': 'Flask'
    }


@app.route('/predict', methods=['POST'])
def predict():
    input_str = request.json.get('str')
    print("DEBUG:",input_str)
    print("DEBUG:type",type(input_str))


    # -----------------给pod发信息(POST 请求）-----------------
    # 发送 POST 请求，直接将 message 作为请求的内容
    response = requests.post(url_POST, data=input_str)

    # 检查响应状态码
    if response.status_code == 200:
        print("POST 请求成功！")
        print("响应内容：", response.text)
    else:
        print("POST 请求失败，状态码：", response.status_code)
    # -----------------给pod发信息(POST 请求）-----------------

    # -----------------从pod抓信息(GET 请求）-----------------
    response = requests.get(url_GET)
    if response.status_code == 200:
        print("pod返回的数据:", response.text)  # 接收返回的字符串数据
    else:
        print('请求失败，状态码:', response.status_code)
    # -----------------从pod抓信息(GET 请求）-----------------
          
    return response.text


@app.route('/evaluation', methods=['GET'])
def evaluation():
    return {
        'Task': 'evaluation',
        'Frontend': 'React',
        'Backend': 'Flask'
    }


@app.route('/work', methods=['POST,GET'])
def work():
    return {
        'Task': 'work',
        'Frontend': 'React',
        'Backend': 'Flask'
    }

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
