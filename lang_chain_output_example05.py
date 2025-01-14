"""
lang_chain_output_example05 -

Author: zhang
Date: 2024/3/13
"""
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv

# 加载当前目录下的.env到系统环境
_ = load_dotenv(find_dotenv())

llm = ChatOpenAI()  # 默认是gpt-3.5-turbo

if __name__ == '__main__':
    response = llm.invoke("你是谁")
    print(response.content)


class Address(BaseModel):
    name: str = Field(description="姓名")
    phone: str = Field(description="手机号")
    province: str = Field(description="省份")
    city: str = Field(description="城市")
    detail: str = Field(description="详细地址")


    @validator("phone")
    def valid_phone(cls, field):
        if len(field) != 11:
            raise ValueError("手机号位数有点问题")
        return field


# Set up a parser + inject instructions into the prompt template.
parser = PydanticOutputParser(pydantic_object=Address)


# if __name__ == '__main__':
#     output = model.invoke("Tell me an express delivery address.")
#     print(output)
#     parser.invoke(output)