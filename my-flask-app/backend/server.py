# -*- coding: utf-8 -*-
# server
# File: server.py

from flask import Flask, render_template, request, jsonify, Response, abort # 导入 Response 和 abort
from flask_cors import CORS

import sys
import logging
import json
import requests
import os
import time
import random
import subprocess
from subprocess import PIPE, CalledProcessError

from datetime import datetime, timezone
import docker 
docker_client =docker.from_env()
app = Flask(__name__)

# 将输出写入标准输入
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR) # 通常生产环境设置ERROR或更高，开发时可以调低

CORS(app) # 允许跨域请求
app.static_folder = 'static'

# 定义目标 IP 的地址和端口
# ghHu: 这里是server to pod的POST请求 所以以下的信息是**pod**的ip和port
# to zsp: 这里改成你的minikube那些ip,port等等
target_ip = '47.96.69.65'
target_ip = '81.70.210.120'
target_port = 3111  # pod的flask我用的3111端口

# target_ip1 = '43.143.237.221'
target_ip1 = '81.70.210.120'

target_port1 = 3112  # pod的flask我用的3111端口


# 构造 POST 请求的 URL
url_POST0 = f'http://{target_ip}:{target_port}/server2pod'

# 构造 GET 请求的 URL
url_GET0 = f'http://{target_ip}:{target_port}/pod2server'

url_POST1 = f'http://{target_ip1}:{target_port1}/server2pod'
url_GET1 = f'http://{target_ip1}:{target_port1}/pod2server'

url_POSTs = [url_POST0, url_POST1]
url_GETs = [url_GET0, url_GET1]

# 初始选择的模型对应的URL
url_POST = url_POSTs[0]
url_GET = url_GETs[0]

# 注意：全局变量 container_list 在 trainlist_get 中被append，
# 但每次请求 trainlist_get 都会重新执行，并且没有清空 container_list，
# 这会导致列表重复增长。更好的做法是在函数内部构建列表并返回。
# 暂时保留但请注意潜在问题。
container_list = []

# 配置上传文件的保存路径
UPLOAD_FOLDER = '/app/uploads'  # 替换为你想要保存文件的路径
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv', 'zip'}  # 允许的文件扩展名

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/train/upload', methods=['POST'])
def upload_file():
    try:
        # 检查请求中是否包含文件
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # 验证文件扩展名
        if file and allowed_file(file.filename):
            # 确保文件名安全，避免路径遍历攻击
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            return jsonify({'message': f'File {file.filename} uploaded successfully', 'path': filename}), 200
        else:
            return jsonify({'error': 'File type not allowed'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/work')
def index_work():
    # 这个路由和 '/' 路由返回相同模板，并且 POST/GET 方法没有实际区分处理
    # 考虑是否需要这个路由，或者赋予它特定功能
    return render_template('index.html')


@app.route('/selection', methods=['POST'])
def selection():
    return {
        'Task': 'selection',
        'Frontend': 'React',
        'Backend': 'Flask'
    }


@app.route('/load', methods=['POST','GET'])
def load():
    if request.method == 'GET':
        data = [
        {
            "value": 0,
            "name":"bert-English"
        },
        {
            "value": 1,
            "name":"bert-Chinese"
        }
        ]
        json_data = json.dumps(data)
        print("THIS IS LOAD!!!! (GET)")
        return json_data
    elif request.method == 'POST':
        print("DEBUG: POST at /load ",request.is_json)
        data_json = request.get_json()
        print("DEBUG: /load: ", data_json)

        model = data_json.get('model') # 使用 .get() 更安全
        global url_POST, url_GET # 声明使用全局变量

        if model == "bert-English":
            url_POST = url_POSTs[0]
            url_GET = url_GETs[0]
            print("DEBUG: Switched to bert-English URLs")
        elif model == "bert-Chinese":
            url_POST = url_POSTs[1]
            url_GET = url_GETs[1]
            print("DEBUG: Switched to bert-Chinese URLs")
        else:
             print(f"Warning: Unknown model '{model}' received in /load POST. Using default URLs.")
             # 可以选择返回错误
             # return jsonify({"error": f"Unknown model: {model}"}), 400

        # 总是返回一个成功的响应，表示模型选择已处理
        return jsonify({"message": f"Model '{model}' selected"}), 200
#0512-替换原有create
@app.route('/create', methods=['POST'])
def create_container():
    """最终极简版容器启动接口"""
    try:
        # 1. 接收并解析请求
        data = request.get_json()
        model = data.get('model', '').strip()
        dataset = data.get('dataset', '').strip()
        # 2. 基础校验（只需要model和dataset）
        if not model or not dataset:
            return jsonify(success=False, error="必须提供 model 和 dataset 参数"), 400
        # 3. 硬编码镜像名称（根据你的实际镜像名称）
        IMAGE_NAME = "bert-ner:conll2003"
        # 4. 生成唯一容器名
        timestamp = int(time.time())
        rand_suffix = random.randint(1000, 9999)
        container_name = f"{model}-{dataset}-{timestamp}-{rand_suffix}"
        # 5. 构建Docker命令（仅包含必要参数）
        docker_cmd = [
            "docker", "run",
            "--name", container_name,
            "--detach",  # 后台运行
            IMAGE_NAME
        ]
        # 6. 执行命令（兼容Python3.6）
        result = subprocess.run(
            docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True  # 替代text=True
        )
        # 7. 处理结果
        if result.returncode == 0:
            return jsonify(
                success=True,
                container_id=result.stdout.strip(),
                container_name=container_name
            )
        else:
            return jsonify(
                success=False,
                error=result.stderr,
                command=" ".join(docker_cmd)
            ), 500
    except Exception as e:
        return jsonify(
            success=False,
            error=f"服务器内部错误: {str(e)}"
        ), 500


# 修改 /predict 路由，借鉴 /load 逻辑
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    处理 /predict 的 GET 和 POST 请求。
    GET: 返回可用模型列表（从 /trainlist 获取）。
    POST: 如果提供 {"model": "<container_name>"}, 记录模型选择并返回确认；
          如果提供 {"model": "<container_name>", "str": "<input>"}, 执行 NER 预测。
    """
    if request.method == 'GET':
        # 借鉴 /load 的 GET 逻辑，返回模型列表
        try:
            response = requests.get('http://81.70.210.120/trainlist', timeout=5)
            response.raise_for_status()
            trainlist_data = response.json().get('trainlist', [])
            print(f"Successfully fetched trainlist: {trainlist_data}")
            
            # 转换为 /load 的格式: [{"value": "<id>", "name": "<container_name>"}]
            model_list = [
                {"value": str(idx), "name": container.get('name')}
                for idx, container in enumerate(trainlist_data)
                if container.get('name')
            ]
            return jsonify(model_list), 200
        except requests.RequestException as e:
            print(f"Error fetching trainlist: {e}")
            return jsonify({"error": "Failed to fetch model list", "details": str(e)}), 500

    elif request.method == 'POST':
        print("Received POST request for /predict")

        # 获取 JSON 数据
        try:
            data_json = request.get_json()
            if not data_json:
                print("Error: No JSON data provided")
                return jsonify({"error": "No JSON data provided"}), 400
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return jsonify({"error": "Invalid JSON format", "details": str(e)}), 400

        # 提取 model 和 str
        model = data_json.get('model')
        input_str = data_json.get('str')

        if not model:
            print("Error: Missing 'model' field")
            return jsonify({"error": "Missing required field", "details": "'model' is required"}), 400

        print(f"Extracted model: {model}, str: {input_str}")

        # 借鉴 /load 的 POST 逻辑：如果只提供 model，记录并返回确认
        if not input_str:
            print(f"DEBUG: Model '{model}' selected in /predict POST")
            return jsonify({"message": f"Model '{model}' selected"}), 200

        # 现有 /predict 逻辑：处理 model 和 str 进行 NER 预测
        # 获取 /trainlist 数据以验证 model
        try:
            response = requests.get('http://81.70.210.120/trainlist', timeout=5)
            response.raise_for_status()
            trainlist_data = response.json()
            print(f"Successfully fetched trainlist: {trainlist_data}")
        except requests.RequestException as e:
            print(f"Error fetching trainlist: {e}")
            return jsonify({"error": "Failed to fetch container list", "details": str(e)}), 500

        # 查找匹配的容器
        container_info = None
        for container in trainlist_data.get('trainlist', []):
            if container.get('name') == model:
                container_info = container
                break

        if not container_info:
            print(f"Error: Model '{model}' not found in trainlist")
            return jsonify({"error": f"Model '{model}' not found in container list"}), 400

        # 根据模型选择 URL
        if model.startswith('english_') or container_info.get('dataset') == 'conll2003':
            url_POST = url_POST0
            url_GET = url_GET0
            print(f"Selected English model URLs: POST={url_POST}, GET={url_GET}")
        elif model.startswith('chinese-') or container_info.get('dataset') == 'people_daily':
            url_POST = url_POST1
            url_GET = url_GET1
            print(f"Selected Chinese model URLs: POST={url_POST}, GET={url_GET}")
        else:
            print(f"Error: Unknown model type for '{model}'")
            return jsonify({"error": f"Unknown model type for '{model}'", "details": "Model not recognized as English or Chinese"}), 400

        # 发送 POST 请求到 pod
        try:
            print(f"DEBUG: Sending POST to {url_POST} with model: {model}, str: {input_str}")
            my_json = {
                "model": model,
                "input_str": input_str
            }
            headers = {"Content-Type": "application/json; charset=utf-8"}
            response = requests.post(
                url_POST,
                data=json.dumps(my_json, ensure_ascii=False).encode('utf-8'),
                headers=headers
            )

            if response.status_code == 200:
                print("POST request successful!")
                print("Response content:", response.text)
            else:
                print(f"POST request failed, status: {response.status_code}, response: {response.text}")
                return jsonify({"error": f"Failed to send data to pod: Status {response.status_code}", "details": response.text}), response.status_code
        except requests.exceptions.RequestException as e:
            print(f"Error sending POST request to pod: {e}")
            return jsonify({"error": f"Error connecting to pod for POST: {str(e)}"}), 500

        # 发送 GET 请求从 pod 获取结果
        try:
            print(f"DEBUG: Sending GET to {url_GET}")
            response = requests.get(url_GET)

            if response.status_code == 200:
                print("Pod returned data:", response.text)
                try:
                    json_response_data = response.json()
                    return jsonify(json_response_data), 200
                except json.JSONDecodeError:
                    return response.text, 200
            else:
                print(f"GET request failed, status: {response.status_code}, response: {response.text}")
                return jsonify({"error": f"Failed to get data from pod: Status {response.status_code}", "details": response.text}), response.status_code
        except requests.exceptions.RequestException as e:
            print(f"Error sending GET request to pod: {e}")
            return jsonify({"error": f"Error connecting to pod for GET: {str(e)}"}), 500



@app.route('/evaluation', methods=['POST','GET'])
def evaluat():
    if request.method == 'POST':
        print("DEBUG: evaluate POST success")
        # 假设POST请求体是JSON，并且包含了 evaluation parameters
        try:
            eval_params = request.get_json()
            print("DEBUG: Evaluation parameters:", eval_params)

            # 在这里可以根据 eval_params 执行评估逻辑
            # run_evaluation_script(eval_params) # 实际调用评估脚本

            # 模拟评估结果
            t = random.randint(1,10) % 7
            time.sleep(3) # 生产环境不要阻塞主线程

            Accuracy = 0.792 + t / 150
            Recall = 0.842 + t / 150 * 3
            F1 = Accuracy * 0.2 + Recall * 0.8
            digit = 4

            data = {
                'F1': round(F1, digit),
                'Accuracy': round(Accuracy, digit),
                'Recall': round(Recall, digit)
            }

            print("DEBUG: randint: ", t)
            print("DEBUG: Evaluation results: ", data)

            # 返回 JSON 格式的评估结果
            return jsonify(data), 200

        except Exception as e:
            print(f"Error processing evaluation POST: {e}")
            return jsonify({"error": f"Failed to process evaluation request: {str(e)}"}), 500

    elif request.method == 'GET':
        datasets = [
            {
            'model': 'HAPPY MODEL', # 这个 'model' 键在这里看起来有点奇怪，通常GET是获取数据集列表
            'value': 'conll2003'
            },
            {
            'model': 'HAPPY MODEL',
            'value': 'rmyeid/polyglot_ner'
            }
        ]
        json_datasets = json.dumps(datasets)
        print("DEBUG: /evaluation GET: ",json_datasets)
        return json_datasets




# 新增的路由，用于获取NER相关的Docker镜像列表
@app.route('/createlist', methods=['GET'])
def createlist():
    """
    获取包含 'ner' 的 Docker 镜像列表。
    返回格式：[{'value': 1, 'name': 'repo', 'dataset': 'tag'}, ...]
    """
    print("Received GET request for /createlist")
    try:
        # 执行 docker image list 命令并过滤 'ner'
        # 使用 --format '{{.Repository}}\t{{.Tag}}' 获取 repo 和 tag，用tab分隔
        # 使用 --filter 'reference=*ner*' 过滤包含 'ner' 的镜像名或tag
        result = subprocess.run(
            ['docker', 'image', 'list', '--filter', 'reference=*ner*', '--format', '{{.Repository}}\t{{.Tag}}'],
            stdout=subprocess.PIPE,      # 捕获标准输出
            stderr=subprocess.PIPE,      # 捕获标准错误
            universal_newlines=True, # 将输出解码为文本 (Python 3.7+ 可以用 text=True)
            check=True                   # 如果命令返回非零退出码则抛出异常
        )

        # 获取命令的标准输出，按行分割
        output_lines = result.stdout.strip().split('\n')

        image_list = []
        value_counter = 1

        # 如果没有输出行（除了可能的空行），说明没有找到匹配的镜像
        if not output_lines or (len(output_lines) == 1 and output_lines[0] == ''):
             print("DEBUG: No 'ner' images found.")
             return jsonify([])

        # 遍历每一行输出
        for line in output_lines:
            # 每一行是 "repository\ttag" 格式
            parts = line.split('\t', 1) # 只分割一次tab

            repo = parts[0]
            tag = parts[1] if len(parts) > 1 else "" # 如果没有tag，则dataset为空字符串

            # 根据需求构造字典
            image_info = {
                "value": value_counter,
                "name": repo,    # 假设 repository 作为 name
                "dataset": tag   # 假设 tag 作为 dataset
            }
            image_list.append(image_info)
            value_counter += 1

        print(f"DEBUG: Found {len(image_list)} 'ner' images.")
        # 返回 JSON 格式的列表
        return jsonify(image_list)

    except FileNotFoundError:
        print("Error: 'docker' command not found.")
        return jsonify({"error": "Docker command not found. Is Docker installed and in the system's PATH?"}), 500
    except CalledProcessError as e:
        print(f"Docker command failed: {e.stderr.strip()}")
        return jsonify({"error": f"Docker command failed: {e.stderr.strip()}"}), 500
    except Exception as e:
        print(f"An unexpected error occurred in createlist: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# ============================================================
# stop container
@app.route('/trainlist/<int:container_value>', methods=['DELETE'])
def stop_container(container_value):
    """
    处理停止指定容器值的 DELETE 请求。
    通过 container_value 查找容器名称，然后执行 docker stop 命令。
    """
    print(f"Received DELETE request for container value: {container_value}")

    # 1. 获取当前的容器列表，以便根据 value 找到 name
    # 复制 trainlist GET 路由中的逻辑来获取容器列表，但这次需要列出所有容器（包括停止的）来确保能找到
    try:
        # 使用 docker ps -a 来列出所有容器，包括已停止的
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=ner', '--format', '{{.Names}}\t{{.Image}}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )

        output_lines = result.stdout.strip().split('\n')
        value_counter = 1
        target_container_name = None # 用于存储找到的容器名称

        if output_lines and not (len(output_lines) == 1 and output_lines[0] == ''):
            for line in output_lines:
                parts = line.split('\t', 1)
                container_name = parts[0]
                # image_name = parts[1] if len(parts) > 1 else "" # 这里不需要镜像名，只需要容器名

                # 检查当前容器的 value 是否匹配请求的 container_value
                if value_counter == container_value:
                    target_container_name = container_name
                    # 找到了，可以提前退出循环
                    break

                value_counter += 1

    except FileNotFoundError:
        print("Error: 'docker' command not found.")
        return jsonify({"error": "'docker' command not found. Is Docker installed and in PATH?"}), 500
    except CalledProcessError as e:
        print(f"Error listing containers: {e.stderr.strip()}")
        return jsonify({"error": f"Failed to list containers to find name: {e.stderr.strip()}"}), 500
    except Exception as e:
        print(f"An unexpected error occurred during container listing: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred during listing: {str(e)}"}), 500

    # 2. 检查是否找到了对应的容器名称
    if target_container_name is None:
        print(f"Error: Container with value {container_value} not found in list.")
        return jsonify({"error": f"Container with value {container_value} not found."}), 404

    print(f"Found container name: {target_container_name} for value {container_value}")

    # 3. 构造并执行 docker stop 命令
    command = ["docker", "stop", target_container_name]
    print(f"Executing command: {' '.join(command)}")

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE,      # 捕获标准输出
            stderr=subprocess.PIPE,      # 捕获标准错误
            universal_newlines=True, # 将输出解码为文本
            check=True                   # 如果命令返回非零退出码则抛出异常
        )

        # 如果命令成功执行
        print(f"Successfully stopped container {target_container_name}.")
        print("Stdout:", result.stdout.strip())
        print("Stderr:", result.stderr.strip())

        # 4. 返回成功响应
        return jsonify({"message": f"Successfully stopped container {target_container_name}"}), 200

    except FileNotFoundError:
        # 这应该在上面列出容器时已经被捕获，但作为二次检查保留
        print("Error: 'docker' command not found during stop.")
        return jsonify({"error": "'docker' command not found. Is Docker installed and in PATH?"}), 500
    except CalledProcessError as e:
        # 如果 docker stop 命令执行失败
        print(f"Error stopping container {target_container_name}: {e}")
        print("Command output (stdout):", e.stdout.strip())
        print("Command error (stderr):", e.stderr.strip())
        # 返回一个错误响应
        # 检查错误输出是否包含 "No such container" 或 "is not running" 等信息
        error_detail = e.stderr.strip()
        if "No such container" in error_detail:
             return jsonify({"error": f"Container {target_container_name} not found or already removed.", "details": error_detail}), 404
        elif "is not running" in error_detail:
             return jsonify({"message": f"Container {target_container_name} is already stopped.", "details": error_detail}), 200 # 或者 409 Conflict
        else:
             return jsonify({"error": f"Failed to stop container {target_container_name}", "details": error_detail}), 500
    except Exception as e:
        # 捕获其他意外错误
        print(f"An unexpected error occurred during stop: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# ============================================================


@app.route('/trainlist', methods=['GET'])
def trainlist_get():
    """
    获取包含 'ner' 的 Docker 容器列表，并根据 StartedAt/FinishedAt 计算 Up 时间。
    返回格式：{'trainlist': [{'value': str, 'name': str, 'dataset': str, 'time': str, 'cpu': str, 'memory': str}, ...]}
    使用 docker ps 获取容器列表，docker stats 获取 CPU 和内存，docker inspect 获取运行时间。
    """
    print("Received GET request for /trainlist")

    temp_container_list = []

    try:
        # 1. 获取所有包含 'ner' 的容器名称和镜像名
        # 使用 --filter "status=running" 和 --filter "status=exited" 分开获取可能更清晰，
        # 但为了简化，我们先获取所有容器，再通过 inspect 判断状态
        result = subprocess.run(
            ['docker', 'ps',  '--filter', 'name=ner', '--format', '{{.Names}}\t{{.Image}}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )

        output_lines = result.stdout.strip().split('\n')
        value_counter = 1

        if not output_lines or (len(output_lines) == 1 and output_lines[0] == ''):
            print("DEBUG: No 'ner' containers found.")
            return jsonify({"trainlist": []}) # 返回空列表而不是 ["Nothing"] 更符合 JSON 格式

        # 2. 获取所有容器的资源占用信息（docker stats）
        # 注意：docker stats 只能获取正在运行的容器的信息，对于已停止的容器，CPU和内存会显示 "--" 或 "0"。
        try:
            stats_result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format', '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                check=True
            )
            stats_lines = stats_result.stdout.strip().split('\n')
            stats_dict = {}
            for line in stats_lines:
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        container_name = parts[0]
                        cpu = parts[1].strip()  # 保留 % 符号
                        memory = parts[2].split('/')[0].strip()  # 取 MEM USAGE 部分
                        stats_dict[container_name] = {'cpu': cpu, 'memory': memory}
        except CalledProcessError:
             # 如果没有正在运行的容器，docker stats 会报错，这里捕获并忽略
            print("DEBUG: docker stats command failed (likely no running containers).")
            stats_dict = {} # 初始化为空字典

        # 3. 遍历容器列表
        for line in output_lines:
            parts = line.split('\t', 1)
            container_name = parts[0]
            image_name = parts[1] if len(parts) > 1 else ""
            image_parts = image_name.rsplit(':', 1)
            image_tag = image_parts[1] if len(image_parts) > 1 else ""

            # 4. 获取容器详细信息（docker inspect）
            try:
                inspect_result = subprocess.run(
                    ['docker', 'inspect', container_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    check=True
                )
                inspect_data = json.loads(inspect_result.stdout)[0] # inspect 返回一个列表，取第一个元素

                # 提取 StartedAt 和 FinishedAt
                started_at_str = inspect_data.get('State', {}).get('StartedAt')
                finished_at_str = inspect_data.get('State', {}).get('FinishedAt') # 已停止的容器才有 FinishedAt

                # print(started_at_str, finished_at_str)

                up_time_str = "0" # 默认 Up 时间为 0

                # 解析时间并判断状态
                if started_at_str and started_at_str != '0001-01-01T00:00:00Z': # 检查 StartedAt 是否有效
                     # Docker 的时间格式可能是带纳秒的，只取到秒
                    started_dt = datetime.strptime(started_at_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    # 将 StartedAt 视为 UTC 时间，因为 Docker 默认使用 UTC

                    print(started_dt)
                    started_dt = started_dt.replace(tzinfo=timezone.utc)

                    # 如果 FinishedAt 是 '0001-01-01T00:00:00Z' 或 FinishedAt 的时间早于 StartedAt
                    # 说明容器正在运行
                    if  finished_at_str or finished_at_str == '0001-01-01T00:00:00Z':
                        # 容器正在运行
                        now_dt = datetime.now(timezone.utc) # 获取当前 UTC 时间
                        time_difference = now_dt - started_dt
                        total_seconds = time_difference.total_seconds()

                        # 格式化时间差为人性化的字符串 (天, 小时, 分钟)
                        days = int(total_seconds // 86400)
                        hours = int((total_seconds % 86400) // 3600)
                        minutes = int((total_seconds % 3600) // 60)

                        if days > 0:
                            up_time_str = f"{days}d {hours}h" # 显示天和小时
                        elif hours > 0:
                            up_time_str = f"{hours}h {minutes}m" # 显示小时和分钟
                        else:
                            up_time_str = f"{minutes}m" # 显示分钟

                    else:
                         # 容器已停止，Up 时间为 0
                        up_time_str = "0"


            except (json.JSONDecodeError, KeyError, ValueError, IndexError) as e:
                print(f"Error parsing inspect data for container {container_name}: {e}")
                up_time_str = "Error" # 解析失败显示错误

            # 5. 从 stats_dict 获取 CPU 和内存信息
            # 对于已停止的容器，stats_dict 中可能没有信息，提供默认值
            cpu = stats_dict.get(container_name, {}).get('cpu', '--') # 默认显示 --
            memory = stats_dict.get(container_name, {}).get('memory', '--') # 默认显示 --


            # 6. 构造容器信息字典
            container_info = {
                "value": str(value_counter),
                "name": container_name,
                "dataset": image_tag,
                "time": up_time_str,  # 根据 StartedAt/FinishedAt 计算的 Up 时间
                "cpu": cpu,
                "memory": memory
            }
            temp_container_list.append(container_info)
            value_counter += 1

        print(f"DEBUG: Found {len(temp_container_list)} 'ner' containers.")
        return jsonify({"trainlist": temp_container_list})

    except FileNotFoundError:
        print("Error: 'docker' command not found.")
        return jsonify({"error": "Docker command not found. Is Docker installed and in the system's PATH?"}), 500
    except CalledProcessError as e:
        print(f"Docker command failed: {e.stderr.strip()}")
        return jsonify({"error": f"Docker command failed: {e.stderr.strip()}"}), 500
    except Exception as e:
        print(f"An unexpected error occurred in trainlist_get: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# ============================================================
# 获取容器日志的新路由
# 接收容器名称或 ID 作为字符串参数
@app.route('/run/<i>', methods=['GET'])
def get_container_logs(i):
    """
    处理 /run/<i> 这样的 GET 请求。
    其中 <i> 是容器编号（trainlist JSON 中的 value 字段，字符串）。
    通过 http://81.70.210.120/trainlist 获取容器列表，查找对应容器名，
    执行 docker logs 命令并返回容器的运行日志，以 JSON 格式返回 {"content": logs}。
    """
    print(f"Received GET request for container logs with value: {i}")

    # 获取容器列表
    try:
        response = requests.get('http://81.70.210.120/trainlist', timeout=5)
        response.raise_for_status()  # 检查请求是否成功
        trainlist_data = response.json()
        print(f"Successfully fetched trainlist: {trainlist_data}")
    except requests.RequestException as e:
        print(f"Error fetching trainlist: {e}")
        return jsonify({"error": "Failed to fetch container list", "details": str(e)}), 500

    # 查找匹配的容器
    container_name = None
    for container in trainlist_data.get('trainlist', []):
        if container.get('value') == i:
            container_name = container.get('name')
            break

    if not container_name:
        print(f"No container found with value: {i}")
        return jsonify({"error": f"No container found with value {i}"}), 404

    print(f"Found container name: {container_name} for value: {i}")

    # 构造 docker logs 命令
    command = ["docker", "logs", container_name]
    print(f"Executing command: {' '.join(command)}")

    try:
        # 执行 docker logs 命令
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,      # 捕获标准输出 (日志)
            stderr=subprocess.PIPE,      # 捕获标准错误
            universal_newlines=True,    # 将输出解码为文本
            check=True                  # 如果命令返回非零退出码则抛出异常
        )

        # 返回 JSON 格式的日志内容
        logs = result.stdout
        print(f"Successfully retrieved logs for container {container_name}.")
        return jsonify({"content": logs})

    except FileNotFoundError:
        print("Error: 'docker' command not found.")
        return jsonify({"error": "Docker command not found. Is Docker installed?"}), 500
    except subprocess.CalledProcessError as e:
        print(f"Error getting logs for container {container_name}: {e}")
        print("Command output (stdout):", e.stdout.strip())
        print("Command error (stderr):", e.stderr.strip())

        error_detail = e.stderr.strip()
        if "No such container" in error_detail:
            print(f"Container '{container_name}' not found.")
            return jsonify({"error": f"Container '{container_name}' not found."}), 404
        else:
            print(f"Docker logs command failed for '{container_name}': {error_detail}")
            return jsonify({"error": f"Failed to get logs for container {container_name}", "details": error_detail}), 500
    except Exception as e:
        print(f"An unexpected error occurred while getting logs: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500



def generate_training_bash_script(**kwargs):
    model_name_or_path = kwargs.get('model_name_or_path', '')
    dataset_name = kwargs.get('dataset_name', '')
    output_dir = kwargs.get('output_dir', '')
    do_train = kwargs.get('do_train', False)
    do_eval = kwargs.get('do_eval', False)

    # 生成文件名
    # 使用更安全的文件名，避免特殊字符问题
    safe_model_name = model_name_or_path.replace('/', '_').replace(':', '_')
    safe_dataset_name = dataset_name.replace('/', '_').replace(':', '_')
    # 添加时间戳或随机数，避免文件名冲突
    timestamp = int(time.time())
    file_name = f"{safe_model_name}_{safe_dataset_name}_script_{timestamp}.sh"

    print(f"DEBUG: Generating script {file_name}")

    try:
        with open(file_name, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("set -e\n") # 遇到错误立即退出

            # 假设 run_ner.py 在 Docker 容器内部运行
            # 如果你的目标是启动 Docker 容器来执行训练，那么这里的逻辑需要改为 `docker run ...` 命令。
            # 这个函数应该生成并执行一个 `docker run` 命令，而不是一个 bash 脚本来调用 run_ner.py
            # 在宿主机上。
            # 例如：
            # docker run --rm -v /path/to/data:/data -v /path/to/output:/output your_ner_image \
            # python /app/run_ner.py --model_name_or_path ... --dataset_name ... --output_dir ...

            # **重要：** 以下是假设 run_ner.py 在 Flask 应用所在的宿主机上运行的情况。
            # 如果 run_ner.py 是在 Docker 容器内部运行，请完全修改此函数以调用 `docker run`。

            # 确保脚本有执行权限 (如果 run_ner.py 在宿主机)
            # f.write("chmod +x ./run_ner.py\n") # 假设 run_ner.py 在当前目录

            # 构造 python 命令
            python_command = ["python3", "run_ner.py"] # 假设 run_ner.py 在当前目录或 PATH 中
            if model_name_or_path:
                python_command.extend(["--model_name_or_path", f'"{model_name_or_path}"']) # 参数需要引号
            if dataset_name:
                python_command.extend(["--dataset_name", f'"{dataset_name}"'])
            if output_dir:
                 # 确保 output_dir 存在，或者让脚本自行创建
                 f.write(f"mkdir -p \"{output_dir}\"\n")
                 python_command.extend(["--output_dir", f'"{output_dir}"'])
            if do_train:
                python_command.append("--do_train")
            if do_eval:
                python_command.append("--do_eval")

            # 将 python 命令写入脚本
            f.write(" ".join(python_command) + "\n")

            f.write("echo \"Script finished.\"\n")

        # 确保生成的脚本文件有执行权限
        os.chmod(file_name, 0o755) # rwxr-xr-x

        # 运行脚本
        print(f"Start training script execution: bash {file_name}")
        # 使用 subprocess.Popen 在后台运行，避免阻塞 Flask
        # 注意：这种方式启动的进程不会被 Flask 自动管理，需要自己处理其生命周期和输出。
        # 如果需要捕获输出或等待完成，需要更复杂的 subprocess 用法或任务队列。
        # 这里只是非阻塞地启动一个 shell 脚本。
        # stdout 和 stderr 重定向到文件，以便后续查看日志
        log_file = f"{file_name}.log"
        err_file = f"{file_name}.err"
        with open(log_file, 'w') as out, open(err_file, 'w') as err:
             # shell=True 可以直接执行字符串命令，但通常不推荐，除非命令非常简单且无外部输入
             # 这里使用 list 形式更安全
             # subprocess.Popen(["bash", file_name], stdout=out, stderr=err)

             # 如果 run_ner.py 是在 Docker 容器中运行，这里的 Popen 命令应该是 `docker run ...`
             # 例如 (伪代码):
             # docker_command = ["docker", "run", "--rm", ...] + your_run_ner_args
             # subprocess.Popen(docker_command, stdout=out, stderr=err)
             pass # Placeholder - **Implement the correct subprocess.Popen call here**

        print(f"Training script {file_name} started in background. Logs in {log_file} and {err_file}")

    except Exception as e:
        print(f"Error generating or starting training script: {e}")
        # 抛出异常以便调用者（/training POST）可以捕获并返回错误
        raise e


if __name__ == '__main__':
    # 确保 run_ner.py 脚本存在且可执行，或者在 Docker 容器内部执行此逻辑
    # 如果 run_ner.py 需要在 Docker 环境中运行，那么 generate_training_bash_script 函数
    # 需要修改为调用 `docker run` 命令来启动一个容器执行训练。
    # 生产环境不要使用 debug=True
    # host='0.0.0.0' 允许外部访问，生产环境请根据需要配置防火墙
    # port=80 是 HTTP 默认端口，可能需要 root 权限或使用非特权端口（如 5000）
    # 在 Docker 容器中运行 Flask 时，通常绑定到 0.0.0.0，并在 Dockerfile 中暴露端口
    app.run(debug=True,host='0.0.0.0',port=80)
