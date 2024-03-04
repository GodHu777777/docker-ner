from transformers import BertForTokenClassification, BertTokenizer
import torch 

# 加载已保存的模型和tokenizer
model = BertForTokenClassification.from_pretrained("/tmp/test-ner")
tokenizer = BertTokenizer.from_pretrained("/tmp/test-ner")

# 输入文本
# TODO: can combine with frontend(FLASK) to make interactive input
text = "John is from New York, United States."

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

# 显示预测结果和实体类型
# TODO: can combine with frontend to make interative output
for token, label_id in zip(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0]), predicted_labels[0]):
    print(f"{token}: {labels[label_map[label_id.item()]]}")

