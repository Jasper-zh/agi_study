import uuid
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage,
)
from langfuse.callback import CallbackHandler
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

llm = ChatOpenAI()

messages = []

handler = CallbackHandler(
    user_id="001",
    session_id="session001"
)

if __name__ == '__main__':
    while True:
        user_input = input("User: ")
        if user_input.strip() == "":
            break
        messages.append(HumanMessage(content=user_input))
        response = llm.invoke(messages, config={"callbacks": [handler]})
        print("AI: " + response.content)
        messages.append(response)
