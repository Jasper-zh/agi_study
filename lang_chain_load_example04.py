"""
lang_chain_load_example04 -

Author: zhang
Date: 2024/3/11
"""
from langchain.prompts import load_prompt
import json
import io
import sys


if __name__ == '__main__':

    # prompt = load_prompt("simple_prompt.yaml")
    # OR
    with open('lang_chain_prompt_template.json', 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)

    with open('lang_chain_prompt_template.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        print(config)


    prompt = load_prompt("lang_chain_prompt_template.yaml") # 目前徐要指定utf-8才能加载中文字符，该库目前没有给出指定的参数入口
    print(prompt.format(x="炸酱面(15元)"))
