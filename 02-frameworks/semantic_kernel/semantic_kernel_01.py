"""
semantic_kernel_example -

Author: zhang
Date: 2024/3/11
"""
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.prompt_template.input_variable import InputVariable
import asyncio
import os
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())
api_key = os.getenv('OPENAI_API_KEY')

# 创建kernel模型
kernel = sk.Kernel()
service_id = "my-gpt3"
model = OpenAIChatCompletion(
    service_id=service_id,
    ai_model_id="gpt-3.5-turbo",
    api_key=api_key,
)
kernel.add_service(model)

# 请求设置
req_settings = kernel.get_service(service_id).get_prompt_execution_settings_class()(service_id=service_id)
req_settings.max_tokens = 1000
req_settings.temperature = 0.7
req_settings.top_p = 0.8

# 提示词模板设置
prompt_template_config = sk.PromptTemplateConfig(
    template="{{$input}}这个城市有什么好玩的地方",
    name="city_point",
    template_format="semantic-kernel",
    input_variables=[
        InputVariable(name="input", description="The user input", is_required=True),
    ],
    execution_settings=req_settings,
)

# 传入提示词创建函数
city_point = kernel.create_function_from_prompt(
    function_name="search_city_point",
    plugin_name="city",
    #prompt="{{$input}}这个城市有什么好玩的地方"
    prompt_template_config=prompt_template_config,
)

if __name__ == '__main__':
    # kernel.invoke(“函数名”，“参数") 是异步的所以本地使用asyncio.run运行
    result = asyncio.run(kernel.invoke(city_point, sk.KernelArguments(input="武汉")))
    print(result)