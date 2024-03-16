from flask import Flask, render_template, request
from transformers import BertForTokenClassification, BertTokenizer
import torch 
import os

app = Flask(__name__)

@app.route('/train', methods=['GET'])
def train():
    os.system("bash run.sh")
    return 'Hello World'
    

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        input_str = request.form['input_str']
        result = your_function(input_str)  # 调用你的函数，并传入用户输入的字符串
        return render_template('index.html', result=result)
    return render_template('index.html')

def your_function(text):

    # 加载已保存的模型和tokenizer
    model = BertForTokenClassification.from_pretrained("/tmp/test-ner")
    tokenizer = BertTokenizer.from_pretrained("/tmp/test-ner")

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
