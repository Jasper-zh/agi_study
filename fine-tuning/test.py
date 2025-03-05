from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 加载模型和tokenizer
# model = AutoModelForCausalLM.from_pretrained("gpt2")  # 测试时用gpt2，训练后替换为checkpoint路径
model = AutoModelForCausalLM.from_pretrained('./output/checkpoint-1067')
model.eval()
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.add_special_tokens({'pad_token': '[PAD]'})  # 保持与训练时一致 （因为gpt2没有自带填充标签）

# 标签映射
named_labels = ['neg', 'pos']

# 待分类文本
text = "The latest superhero film was a complete disaster. The plot made no sense, the acting was wooden, and the special effects looked cheap and unrealistic. I wasted two hours of my life that I'll never get back. Save your money and avoid this terrible movie at all costs."
inputs = tokenizer(text + tokenizer.eos_token, return_tensors="pt")

# 推理预测
with torch.no_grad():
    output = model.generate(**inputs, do_sample=False, max_new_tokens=1)

# 获取预测的标签token并解码
predicted_token = output[0][-1].item()
label_tokens = [tokenizer(label, add_special_tokens=False)["input_ids"][0] for label in named_labels]

# 判断输出的标签是否在指定的标签
predicted_label = named_labels[label_tokens.index(predicted_token)] if predicted_token in label_tokens else "未知"

print(f"文本: {text}")
print(f"预测标签: {predicted_label}")