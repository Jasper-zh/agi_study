#!/usr/bin/env python
from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langserve import add_routes
import uvicorn


from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple api server using Langchain's Runnable interfaces",
)

model = ChatOpenAI()
promptTemplate = ChatPromptTemplate.from_template("讲一个关于{topic}的笑话")
promptTemplate02 = ChatPromptTemplate.from_template("讲一个关于{city}的历史")
add_routes(
    app,
    promptTemplate | model,
    path="/joke",
)
add_routes(
    app,
    promptTemplate02 | model,
    path="/city/his",
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=9999)