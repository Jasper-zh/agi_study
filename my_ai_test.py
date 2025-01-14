"""
openai -

Author: zhang
Date: 2024/1/19
"""
import json
from sys import displayhook
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# 加载当前目录下的.env到系统环境
_ = load_dotenv(find_dotenv())
# 配置 OpenAI 服务 （从系统环境读取）
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)
# 任务描述
instruction = """
你的任务是识别用户对手机流量套餐产品的选择条件。
每种流量套餐产品包含三个属性：名称(name)，月费价格(price)，月流量(data)。
根据对话上下文，识别用户在上述属性上的倾向。识别结果要包含整个对话的信息。
"""

# 任务背景
background = """
目前运营商有如下的流量包产品：
|   名称   | 流量（G/月） | 价格（元/月） | 适用人群 |
| :------: | -----------: | ------------: | :------: |
| 经济套餐 |           10 |            50 |  无限制  |
| 畅游套餐 |          100 |           180 |  无限制  |
| 无限套餐 |         1000 |           300 |  无限制  |
| 校园套餐 |          200 |           150 |  在校生  |
"""

# 输出格式
output_format = """
以JSON格式输出。
1. name字段的取值为string类型，取值必须为以下之一：经济套餐、畅游套餐、无限套餐、校园套餐 或 null；

2. price字段的取值为一个结构体 或 null，包含两个字段：
(1) operator, string类型，取值范围：'<='（小于等于）, '>=' (大于等于), '=='（等于）
(2) value, int类型

3. data字段的取值为取值为一个结构体 或 null，包含两个字段：
(1) operator, string类型，取值范围：'<='（小于等于）, '>=' (大于等于), '=='（等于）
(2) value, int类型或string类型，string类型只能是'无上限'

4. 用户的意图可以包含按price或data排序，以sort字段标识，取值为一个结构体：
(1) 结构体中以"ordering"="descend"表示按降序排序，以"value"字段存储待排序的字段
(2) 结构体中以"ordering"="ascend"表示按升序排序，以"value"字段存储待排序的字段

只输出中只包含用户提及的字段，不要猜测任何用户未直接提及的字段。不要输出值为null的字段。
"""

# 举个例子
examples = """
客服：有什么可以帮您
用户：100G套餐有什么

{"data":{"operator":">=","value":100}}

客服：有什么可以帮您
用户：100G套餐有什么
客服：我们现在有无限套餐，不限流量，月费300元
用户：太贵了，有200元以内的不

{"data":{"operator":">=","value":100},"price":{"operator":"<=","value":200}}

客服：有什么可以帮您
用户：便宜的套餐有什么
客服：我们现在有经济套餐，每月50元，10G流量
用户：100G以上的有什么

{"data":{"operator":">=","value":100},"sort":{"ordering"="ascend","value"="price"}}

客服：有什么可以帮您
用户：100G以上的套餐有什么
客服：我们现在有畅游套餐，流量100G，月费180元
用户：流量最多的呢

{"sort":{"ordering"="descend","value"="data"},"data":{"operator":">=","value":100}}
"""

# 用户输入
input_text = """
你们店最贵的套餐是什么
"""

# 多轮对话上下文
context = f"""
客服：有什么可以帮您
用户：有什么100G以上的套餐推荐
客服：我们有畅游套餐和无限套餐，您有什么价格倾向吗
用户：{input_text}
"""

def get_completion(prompt):
    response = client.chat.completions.create(
        model='gpt-4',
        messages=[{"role": "user", "content": prompt}],
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
        stream=True     # 流式响应
    )
    # return response.choices[0].message.content  # 返回模型生成的文本
    word = ""
    for res in response:
        cur = res.choices[0].delta.content
        if cur is not None:
            word += cur
        print(word)
    return word


if __name__ == '__main__':
    # prompt 模版。instruction 和 input_text 会被替换为上面的内容
    prompt = f"""
        {instruction}
        任务背景：
        {background}
        输出格式：
        {output_format}
        用户输入：
        {context}
    """
    # 调用大模型
    print(os.environ.get("OPENAI_API_KEY"))
    response = get_completion(prompt)
    print(response)

