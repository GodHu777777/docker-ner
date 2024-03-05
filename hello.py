from flask import Flask
from transformers import BertForTokenClassification, BertTokenizer
import torch 

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f'Post {post_id}'


# 加载已保存的模型和tokenizer
model = BertForTokenClassification.from_pretrained("/tmp/test-ner")
tokenizer = BertTokenizer.from_pretrained("/tmp/test-ner")

# 输入文本
# TODO: can combine with frontend(FLASK) to make interactive input
# text is the input function

@app.route('/string/<string:text>')
def func(text):
    
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

    # initialize result string
    res = ""

    # 显示预测结果和实体类型
    # TODO: can combine with frontend to make interative output
    for token, label_id in zip(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]), predicted_labels[0]):
        res += f"{token}: {labels[label_map[label_id.item()]]}" + "; "

    return res



