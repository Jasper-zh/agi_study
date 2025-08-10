"""
对于添加标注后的数据集进行准确率测试
"""
import threading
from concurrent.futures import ThreadPoolExecutor

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langfuse import Langfuse

from dotenv import load_dotenv, find_dotenv
import os

from langfuse.decorators import langfuse_context

_ = load_dotenv(find_dotenv())  # 加载.env进环境变量

langfuse = Langfuse()
lock = threading.Lock()


def simple_evaluation(output, expected_output):
    return output == expected_output


def run_evaluation(chain, dataset_name, run_name):
    dataset = langfuse.get_dataset(dataset_name)

    def process_item(item):
        with lock:
            handler = item.get_langchain_handler(run_name=run_name)

        output = chain.invoke(item.input, config={"callbacks": [handler]})
        handler.trace.score(name="accuracy", value=simple_evaluation(output, item.expected_output))
        print('.', end='', flush=True)

    # with ThreadPoolExecutor(max_workers=4) as executor:
    #     executor.map(process_item, dataset.items)
    for item in dataset.items:
        process_item(item)


if __name__ == '__main__':
    template = """
    请讲一个关于{context}的故事
    注意字数限制不能超过{num}个汉字
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 获取大模型
    llm = ChatOpenAI(temperature=0)  # 发散性为0 无需传参密钥公钥都从环境变量读取了

    # 构建链式调用器
    chain = (
            {"context": RunnablePassthrough(), "num": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )
    run_evaluation(chain, "my_first_dataset", "first_test")
    langfuse_context.flush()
