import requests
import json
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())
# 初始化 OpenAI 服务
client = OpenAI()  # openai >= 1.3.0 起，OPENAI_API_KEY 和 OPENAI_BASE_URL 会被默认使用

import time


def running(run, thread):
    """等待 run 结束，返回 run 对象，和成功的结果"""
    while run.status == "queued" or run.status == "in_progress":
        """还未中止，再查一次获取最新run信息"""
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id)
        print("status: " + run.status)
        # 等待 1 秒
        time.sleep(1)
        # 递归调用，直到 run 结束
        return running(run, thread)

    if run.status == "completed":
        """成功"""
        # 获取全部消息
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        # 最后一条消息排在第一位
        result = messages.data[0].content[0].text.value
        return run, result
    # 执行失败
    return run, None

if __name__ == '__main__':
    # 创建thread
    thread = client.beta.threads.create(
        metadata= {"uid": 29, "username": "zhangsan", "age": 18}
    )
    print(thread)

    # 创建一个消息在thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,  # message 必须归属于一个 thread
        role="user",  # assistant回复的消息会自动加入到thread，一般只需要创建user的消息进去即可
        content="你是谁呀",
    )
    print(message)

    # assistant id 从 https://platform.openai.com/assistants 获取。你需要在自己的 OpenAI 创建一个
    assistant_id = "asst_KpC6ehe9IjPrnSFYJCiaErS8"

    # 创建一次run
    run = client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=thread.id,
    )
    print(run)

    # 对当前run进行监控
    res = running(run,thread)
    print(res[1])

