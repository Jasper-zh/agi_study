from openai import OpenAI
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv()) # 加载.env进环境变量
client = OpenAI()  # openai >= 1.3.0 起，OPENAI_API_KEY 和 OPENAI_BASE_URL 会被默认使用

if __name__ == '__main__':
    # thread = client.beta.threads.create(metadata={'uid': 28, 'username': 'zhangsan', 'age': 18})
    thread = client.beta.threads.retrieve("thread_jBhNotPx9BYztUdHpSIRLed5")
    print(thread)
    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content="hello 呀")
    print(message)
