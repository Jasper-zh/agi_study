"""
semantic_kernel_example -

Author: zhang
Date: 2024/3/11
"""
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
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

my_plugins = kernel.import_plugin_from_prompt_directory(".", "plugins")

if __name__ == '__main__':
    result = asyncio.run(kernel.run_async(
        my_plugins["city_point"],
        input_vars=["wuhan"],
    ))
    print(result)