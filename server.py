# server
# File: server.py

# here server port is 5000

from flask import Flask, render_template, request
import os
import requests

# 定义目标 IP 的地址和端口
# ghHu: 这里是server to pod的POST请求 所以以下的信息是**pod**的ip和port
# to zsp: 这里改成你的minikube那些ip,port等等 
target_ip = '81.70.210.120'
target_port = 3111  # pod的flask我用的3111端口

# 构造 POST 请求的 URL
url_POST = f'http://{target_ip}:{target_port}/server2pod'

# 构造 GET 请求的 URL
url_GET = f'http://{target_ip}:{target_port}/pod2server'


app = Flask(__name__)

@app.route('/train', methods=['GET'])
def train():
    os.system("bash run.sh")
    return 'Hello World'

message = "Hello from server"

# 点按钮
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        
        # TODO:
        # hgh: 
        # to dlc: 这里的input_str就是要predict的那个句子，你把你的react放进来
        input_str = request.form['input_str']

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
        
        
        return render_template('index.html', result=response.text)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug = True, port=80)
