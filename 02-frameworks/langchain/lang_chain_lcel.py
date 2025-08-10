from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from langchain_core.runnables import RunnablePassthrough

_ = load_dotenv(find_dotenv())


model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)
# Define your desired data structure.
class address(BaseModel):
    name: str = Field(description="姓名")
    phone: str = Field(description="手机号")
    province: str = Field(description="省份")
    city: str = Field(description="城市")
    details: str = Field(description="详细地址")

    @validator("phone")
    def question_ends_with_question_mark(cls, field):
        if len(field) != 11:
            raise ValueError("手机号长度不对呀")
        return field


# Set up a parser + inject instructions into the prompt template.
parser = PydanticOutputParser(pydantic_object=address)

prompt = PromptTemplate(
    template="中文回答用户问题.：\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

if __name__ == '__main__':
    # LCEL 表达式
    runnable = (
            {"query": RunnablePassthrough()} | prompt | model | parser
    )

    # 运行
    ret = runnable.invoke("帮我寄给Jasper，武汉江汉区泛海创业中心，电话14534567890。")
    print(ret.json())
