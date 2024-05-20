# server
# File: server.py

from flask import Flask, render_template
from flask import request
from flask import jsonify

import json
import requests
from flask_cors import CORS

import os

app = Flask(__name__)
CORS(app) # 允许跨域请求
app.static_folder = 'static'

# 定义目标 IP 的地址和端口
# ghHu: 这里是server to pod的POST请求 所以以下的信息是**pod**的ip和port
# to zsp: 这里改成你的minikube那些ip,port等等 
target_ip = '127.0.0.1'
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
@app.route('/load', methods=['GET'])
def load():
    global json_data
    data = [
    {
        "value": 1,
        "name":"model1"
    },
    {
        "value": 2,
        "name":"model2"
    }
    ]
    json_data = json.dumps(data)
    print("THIS IS LOAD!!!!")
    return json_data

@app.route('/training', methods=['GET','POST'])
def training():
    
    if request.method == 'POST':
        if request.is_json:
            # 获取请求体中的JSON数据
            print("DEBUG: JSON, YES!!!")
            data_json = request.get_json()
            # 打印接收到的数据，或在此处处理数据
            print("DEBUG: training parameter by POST: ",data_json)

            data_dict = data_json
            data_list = list(data_dict.values())
            
            model_name_or_path = data_list[0] 
            dataset_name = data_list[1]
            print(type(data_list[0]))
            print(type(data_list[1]))
            generate_training_bash_script(model_name_or_path = model_name_or_path, dataset_name = dataset_name)

            print("DEBUG: convert to list: ", data_list)
            # 返回响应，表示成功接收数据
            return jsonify({"message": "Data received successfully"}), 200
        else:
            # 返回错误响应，表示请求体不是JSON格式
            return jsonify({"error": "Invalid content type. JSON expected."}), 400
    
    elif request.method == 'GET': #GET request
        training_data = [
        {
            "value": 1,
            "name":"modellll1",
            "dataset":"dat"
        },
        {
            "value": 2,
            "name":"model2",
            "dataset":"dataset2"
        },
        {
            "value": 3,
            "name":"model3",
            "dataset":"dataset3"
        }
        ]
        json_training_data = json.dumps(training_data)
        print("DEBUG: json_training_data: ",json_training_data)
        
        return json_training_data



@app.route('/predict', methods=['POST'])
def predict():
    input_str = request.json.get('str')
    print("DEBUG: sentence by POST",input_str)
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

    print("DEBUG: \'/predict\' return value type: ",type(response.text))  
    return response.text


@app.route('/evaluation', methods=['POST','GET'])
def evaluation():
    if request.method == 'POST':
        print("DEBUG: evaluate POST success")
        data = {
                'F1': 223,
                'Accuracy': 124,
                'Recall': 1234
        }
        json_data = json.dumps(data)
        print("DEBUG: ",json_data)
        return json_data


@app.route('/work', methods=['POST','GET'])
def work():
    return {
        'Task': 'work',
        'Frontend': 'React',
        'Backend': 'Flask'
    }

def generate_training_bash_script(**kwargs):
    model_name_or_path = kwargs.get('model_name_or_path', '')
    dataset_name = kwargs.get('dataset_name', '')
    output_dir = kwargs.get('output_dir', '')
    do_train = kwargs.get('do_train', False)
    do_eval = kwargs.get('do_eval', False)

    # 生成文件名
    file_name = f"{model_name_or_path}_{dataset_name}_script.sh"
    print("DEBUG file_name: ", file_name)
    with open(file_name, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("python3 run_ner.py \\\n")
        if model_name_or_path:
            f.write(f"  --model_name_or_path {model_name_or_path} \\\n")
        if dataset_name:
            f.write(f"  --dataset_name {dataset_name} \\\n")
        if output_dir:
            f.write(f"  --output_dir {output_dir} \\\n")
        if do_train:
            f.write("  --do_train \\\n")
        if do_eval:
            f.write("  --do_eval \\\n")
    
    # 运行脚本
    print("Start training...")
    print("DEBUG1 file_name: ", file_name)
    os.system(f"bash {file_name}")

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=80)
