from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory, ConversationTokenBufferMemory
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv

def memory():
    history = ConversationBufferMemory()
    history.save_context({"input": "在？"}, {"output": "在的"})
    print(history.load_memory_variables({}))
    history.save_context({"input": "在干嘛"}, {"output": "在吃饭"})
    print(history.load_memory_variables({}))

def window_memory():
    history = ConversationBufferWindowMemory(k=2)
    history.save_context({"input": "在？"}, {"output": "在的"})
    history.save_context({"input": "在干嘛"}, {"output": "在吃饭"})
    history.save_context({"input": "吃完了叫我"}, {"output": "no problem"})
    print(history.load_memory_variables({}))


_ = load_dotenv(find_dotenv())
model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)
def token_memory():
    history = ConversationTokenBufferMemory(
        llm=model,
        max_token_limit=51
    )
    history.save_context({"input": "在？"}, {"output": "在的"})
    history.save_context({"input": "在干嘛"}, {"output": "在吃饭"})
    history.save_context({"input": "吃完了叫我"}, {"output": "no problem"})
    print(history.load_memory_variables({}))
    return history

if __name__ == '__main__':
    history = token_memory()