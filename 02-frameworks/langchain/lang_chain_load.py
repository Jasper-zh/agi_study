from langchain.prompts import load_prompt


if __name__ == '__main__':
    prompt = load_prompt("prompt_file.json") # 内部打开文件需要要指定utf-8才能加载中文字符，该库目前没有给出指定的参数入口
    print(prompt.format(x="炸酱面(15元)"))