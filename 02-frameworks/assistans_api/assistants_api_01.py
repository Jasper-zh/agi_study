from openai import OpenAI
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv()) # 加载.env进环境变量
client = OpenAI()  # openai >= 1.3.0 起，OPENAI_API_KEY 和 OPENAI_BASE_URL 会被默认使用

if __name__ == '__main__':
    thread01 = client.beta.threads.create()
    print(thread01)
    thread02 = client.beta.threads.create(metadata={'uid': 28, 'username': 'zhangsan', 'age': 18})
    print(thread02)
    client.beta.threads.update("thread_04AVBrzreDQFG35BDpIKXFlS", metadata={'age': 20})
    thread03 = client.beta.threads.retrieve("thread_04AVBrzreDQFG35BDpIKXFlS")
    print(thread03)
    client.beta.threads.delete("thread_atcflNiyt5oAkbMzqe7m5bzF")
