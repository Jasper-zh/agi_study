from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.tools.render import render_text_description


class AutoGPT:
    def __init__(self,llm):
        self.llm = llm
        # 文件目录
        self.work_dir: str = "./auto_gpt_file"
        self.main_prompt_file: str = "./auto_gpt_file/prompts/main.txt"
        self.final_prompt_file: str = "./auto_gpt_file/prompts/final_step.txt"
        # 输出解析器
        self.output_parser = PydanticOutputParser(pydantic_object=Action)
        self.robust_parser = OutputFixingParser.from_llm(parser=self.output_parser, llm=self.llm)
        # 工具集合
        self.tools = []
        # 初始化提示词模板和chain
        self.__init_prompt_templates()
        self.__init_chains()


    def __init_prompt_templates(self):
        # 读取模板并填充模板的几个参数
        self.main_prompt = PromptTemplate.from_file(
            self.main_prompt_file
        ).partial(
            work_dir=self.work_dir,
            tools=render_text_description(self.tools), # 按工具集生成对应提示词描述
            format_instructions=self.output_parser.get_format_instructions() # 输出解析器生成的提示词描述
        )
        # 读取提示词模板
        self.final_prompt = PromptTemplate.from_file(
            self.final_prompt_file
        )

    # 初始化两个提示词模板对应的两个chain
    def __init_chains(self):
        # 主流程的chain
        self.main_chain = (self.main_prompt | self.llm | StrOutputParser())
        # 最终一步的chain
        self.final_chain = (self.final_prompt | self.llm | StrOutputParser())

    # 执行主流程chain，给出结果
    def __step(self,task_description,short_memory,long_memory):
        response = ""
        for s in self.main_chain.stream({
            "task_description": task_description,
            "short_memory": short_memory,
            "long_memory": long_memory
        }):
            response += s
        return response

    def run(self,task_description) -> str:
        # 初始化短时记忆&长记忆
        #short_memory = self.__init_short_memory()
        #long_memory = self.__init_long_memory()
        short_memory = []
        long_memory = []
        # 定义思考步数
        thought_step_count = 0

        while True:
            # 开始执行 (传入传入短记忆长记忆容器和任务描述，得到响应)
            action, response = self.__step(task_description=task_description,
                    short_memory=short_memory,
                    long_memory=long_memory)

            print(response)
            # 如果__step给到的结果action是finish了，则不再执行主流程，跳出执行最终响应
            if action.name == "FINISH":
                break

            self.__exec_action(action)




from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# 用来输出格式化的类：当大模型需要使用外部工具，提供的工具名称和参数信息，用这个类封装
class Action(BaseModel):
    name: str = Field(description="工具或指令名称")
    args: Optional[Dict[str, Any]] = Field(description="工具或指令参数，由参数名称和参数值组成")



if __name__ == '__main__':
    from dotenv import load_dotenv, find_dotenv
    _ = load_dotenv(find_dotenv())
    llm = ChatOpenAI()
    auto_gpt = AutoGPT(llm=llm)
    auto_gpt.run(task_description="今天的天气怎么样")