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

kernel = sk.Kernel()

api_key = os.getenv('OPENAI_API_KEY')
service_id = "my-gpt3"
model = OpenAIChatCompletion(
    service_id=service_id,
    ai_model_id="gpt-3.5-turbo",
    api_key=api_key,
)

kernel.add_service(model)

req_settings = kernel.get_service(service_id).get_prompt_execution_settings_class()(service_id=service_id)
req_settings.max_tokens = 2000
req_settings.temperature = 0.7
req_settings.top_p = 0.8
prompt_template_config = sk.PromptTemplateConfig(
    template="tell me a joke about {{$input}}",
    name="tell_joke_about",
    template_format="semantic-kernel",
    input_variables=[
        InputVariable(name="input", description="The user input", is_required=True),
    ],
    execution_settings=req_settings,
)

tell_joke_about = kernel.create_function_from_prompt(
    function_name="tell_joke_about",
    plugin_name="tell",
    prompt_template_config=prompt_template_config,
)


if __name__ == '__main__':
    result = asyncio.run(kernel.invoke(tell_joke_about, sk.KernelArguments(input="hello world")))
    print(result)