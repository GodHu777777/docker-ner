# server
# File: server.py

# here server port is 5000

from flask import Flask, render_template, request
from transformers import BertForTokenClassification, BertTokenizer
import torch 
import os
import requests

# 定义目标 IP 的地址和端口
# ghHu: 这里是server to pod的POST请求 所以以下的信息是**pod**的ip和port
target_ip = '127.0.0.1'
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
        
        
        result = your_function(input_str)  # 调用你的函数，并传入用户输入的字符串
        return render_template('index.html', result=result)
    return render_template('index.html')

def your_function(text):

    # 加载已保存的模型和tokenizer
    model = BertForTokenClassification.from_pretrained("/home/ghhu/study/docker/docker-ner/test-ner")
    tokenizer = BertTokenizer.from_pretrained("/home/ghhu/study/docker/docker-ner/test-ner")

    # 输入文本
    # TODO: can combine with frontend(FLASK) to make interactive input
    # Done

    # 对输入文本进行标记化
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    # 进行预测
    with torch.no_grad():
        outputs = model(**inputs)

    # 处理预测结果
    predicted_labels = torch.argmax(outputs.logits, axis=-1)

    # 获取实体类型标签映射
    label_map = {i: label for i, label in enumerate(model.config.id2label)}

    # label_id to label
    labels = ['O', 'B-PER', 'I-PER', 'B-ORG', 'I-ORG', 'B-LOC', 'I-LOC', 'B-MISC', 'I-MISC']

    res = ""

    # 显示预测结果和实体类型
    # TODO: can combine with frontend to make interative output
    for token, label_id in zip(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]), predicted_labels[0]):
        print(f"{token}: {labels[label_map[label_id.item()]]}")
        res += f"{token}: {labels[label_map[label_id.item()]]}" + "  " 
    
    return res

    
# receive message from pod
@app.route('/pod2server', methods=['POST'])
def receiveFromPod():
    if request.method == 'POST':
        # 从 POST 请求中获取消息内容
        message = request.data.decode('utf-8')
        print(type(message))
        print("Received message:", message)
        return "Message received successfully!", 200
    else:
        return "Only POST requests are allowed", 405

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug = True, port=5000)
