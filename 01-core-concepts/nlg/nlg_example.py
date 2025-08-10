"""
nlg_example -

Author: zhang
Date: 2024/1/26
"""

import json
import copy
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = OpenAI()

instruction = """
你的任务是识别用户对手机流量套餐产品的选择条件。
每种流量套餐产品包含三个属性：名称(name)，月费价格(price)，月流量(data)。
根据用户输入，识别用户在上述三种属性上的倾向。
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

只输出中只包含用户提及的字段，不要猜测任何用户未直接提及的字段。
DO NOT OUTPUT NULL-VALUED FIELD! 确保输出能被json.loads加载。
"""

examples = """
便宜的套餐：{"sort":{"ordering"="ascend","value"="price"}}
有没有不限流量的：{"data":{"operator":"==","value":"无上限"}}
流量大的：{"sort":{"ordering"="descend","value"="data"}}
100G以上流量的套餐最便宜的是哪个：{"sort":{"ordering"="ascend","value"="price"},"data":{"operator":">=","value":100}}
月费不超过200的：{"price":{"operator":"<=","value":200}}
就要月费180那个套餐：{"price":{"operator":"==","value":180}}
经济套餐：{"name":"经济套餐"}
"""


class NLU:
    # 初始化NLU类，设置对话系统的模板，内容包含任务说明、输出格式、用户输入示例等信息
    def __init__(self):
        self.prompt_template = f"{instruction}\n\n{output_format}\n\n{examples}\n\n用户输入：\n__INPUT__"

    # 发送用户输入到OpenAI GPT模型，获取模型的响应
    def _get_completion(self, prompt, model="gpt-3.5-turbo"):
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,  # 模型输出的随机性，0 表示随机性最小
        )
        print(response.choices[0].message.content)
        semantics = json.loads(response.choices[0].message.content)
        return {k: v for k, v in semantics.items() if v}

    # 拼接上用户输入，调用上面的私有方法 _get_completion 获取语义解析
    def parse(self, user_input):
        prompt = self.prompt_template.replace("__INPUT__", user_input)
        return self._get_completion(prompt)


class DST:
    def __init__(self):
        pass

    # 根据NLU解析得到的语义信息，更新对话状态
    def update(self, state, nlu_semantics):
        # 本次语义指定了名称不需要之前的状态了
        if "name" in nlu_semantics:
            state.clear()
        # 本次语义存在了一项排序且就是等于，那么状态中关于该项的排序可删除了
        if "sort" in nlu_semantics:
            slot = nlu_semantics["sort"]["value"]
            if slot in state and state[slot]["operator"] == "==":
                del state[slot]
        # 将本次语义存入状态
        for k, v in nlu_semantics.items():
            state[k] = v
        return state

# MockedDB类，用于模拟数据库，提供流量套餐的数据
class MockedDB:
    # 初始化模拟数据库，包含一些流量套餐的信息
    def __init__(self):
        self.data = [
            {"name": "经济套餐", "price": 50, "data": 10, "requirement": None},
            {"name": "畅游套餐", "price": 180, "data": 100, "requirement": None},
            {"name": "无限套餐", "price": 300, "data": 1000, "requirement": None},
            {"name": "校园套餐", "price": 150, "data": 200, "requirement": "在校生"},
        ]

    # 模拟数据库查询，从状态里的信息，查询数据库对应的一条记录
    def retrieve(self, **kwargs):
        # 初始化一个空列表，用于存储选择的记录
        records = []

        # 遍历数据中的每个记录
        for r in self.data:
            # 初始化一个标志，用于确定是否选择该记录
            select = True

            # 检查记录是否具有"requirement"字段
            if r["requirement"]:
                # 如果"status"不在kwargs中或与要求不匹配，则跳过此记录
                if "status" not in kwargs or kwargs["status"] != r["requirement"]:
                    continue

            # 遍历kwargs中的键值对
            for k, v in kwargs.items():
                # 跳过"sort"键
                if k == "sort":
                    continue

                # 如果键是"data"且值为"无上限"
                if k == "data" and v["value"] == "无上限":
                    # 语义里的无上限实际对应的是数据库里流量为1000的套餐
                    if r[k] != 1000:
                        select = False
                        break

                # 如果值中包含"operator"键
                if "operator" in v:
                    # 使用eval函数进行动态运算，检查是否满足条件
                    # 当前记录的data/price <= 100 如果不是跳出
                    if not eval(str(r[k])+v["operator"]+str(v["value"])):
                        select = False
                        break

                # 如果值不包含"operator"键，直接比较值
                # 有可能data或者price对应直接就是值而不是一个结构体
                elif str(r[k]) != str(v):
                    select = False
                    break

            # 如果以上筛选条件都未淘汰，则将其添加到records列表中
            if select:
                records.append(r)

        # 如果records列表长度小于等于1，直接返回
        if len(records) <= 1:
            return records

        # 上面的循环选出了满足筛选条件的记录，现在开始根据排序参数对records进行排序
        key = "price"
        reverse = False
        if "sort" in kwargs:
            # 排序的字段
            key = kwargs["sort"]["value"]
            # 是否降序
            reverse = kwargs["sort"]["ordering"] == "descend"
            # 里面的记录按key字段（data/price）排序，排序方式 False/True (升序/降序)
        return sorted(records, key=lambda x: x[key], reverse=reverse)


# DialogManager类，用于管理整个对话流程
class DialogManager:
    def __init__(self, prompt_templates):
        self.state = {}
        # 字段初始化赋值，对话session：初始内容一段设定，并且以system角色发出优先级更高
        self.session = [
            {
                "role": "system",
                "content": "你是一个手机流量套餐的客服代表，你叫小瓜。可以帮助用户选择最合适的流量套餐产品。"
            }
        ]
        # 字段初始化赋值：语义解析器
        self.nlu = NLU()
        # 字段初始化赋值：状态跟踪器
        self.dst = DST()
        # 字段初始化赋值：数据库
        self.db = MockedDB()
        # 字段初始化赋值：语言模板字符串
        self.prompt_templates = prompt_templates

    # 根据模型的回复和数据库的结果，生成用户最终看到的回复
    def _wrap(self, user_input, records):
        if records:
            prompt = self.prompt_templates["recommand"].replace(
                "__INPUT__", user_input)
            # 选第一条套餐回给用户
            r = records[0]
            for k, v in r.items():
                # 根据您的需求，推荐您选择__NAME__套餐，月费为__PRICE__元，流量为__DATA__GB。
                # 将套餐的一些字段，替换到模板当中
                prompt = prompt.replace(f"__{k.upper()}__", str(v))
        else:
            prompt = self.prompt_templates["not_found"].replace(
                "__INPUT__", user_input)
            for k, v in self.state.items():
                # 如果没有匹配项，使用另一个模板
                # 抱歉，找不到符合条件的套餐，请重新提出您的需求。您说的是__INPUT__吗？
                if "operator" in v:
                    prompt = prompt.replace(
                        # 将某个字段占位，换成类似 <= 100
                        f"__{k.upper()}__", v["operator"]+str(v["value"]))
                else:
                    # 如果语义状态里没有operator，那就直接用value
                    prompt = prompt.replace(f"__{k.upper()}__", str(v))
        return prompt

    # 调用OpenAI GPT模型生成回复
    def _call_chatgpt(self, prompt, model="gpt-3.5-turbo"):
        session = copy.deepcopy(self.session)
        # 往对话session中添加一条消息
        session.append({"role": "user", "content": prompt})
        # 再将整个对话session发送给大模型
        response = client.chat.completions.create(
            model=model,
            messages=session,
            temperature=0,
        )
        # 返回大模型响应结果
        return response.choices[0].message.content

    # 主要对话流程，包括NLU解析、DST状态更新、数据库查询、GPT模型调用等步骤
    def run(self, user_input):
        # 调用NLU获得语义解析
        semantics = self.nlu.parse(user_input)
        print("===semantics 语义===")
        print(semantics)

        # 调用DST更新多轮状态
        self.state = self.dst.update(self.state, semantics)
        print("===state 语义状态===")
        print(self.state)

        # 根据状态检索DB，获得满足条件的候选 (按照条件排好了顺序，基本上取第一个当作最匹配)
        records = self.db.retrieve(**self.state)

        # 拼装prompt
        prompt_for_chatgpt = self._wrap(user_input, records)
        print("===gpt-prompt 拼接prompt===")
        print(prompt_for_chatgpt)

        # 调用chatgpt获得回复
        response = self._call_chatgpt(prompt_for_chatgpt)

        # 将当前用户输入和系统回复维护入对话session
        self.session.append({"role": "user", "content": user_input})
        self.session.append({"role": "assistant", "content": response})
        return response


