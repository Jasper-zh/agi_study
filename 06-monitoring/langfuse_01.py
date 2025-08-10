import os
import time
import requests
from langfuse.openai import openai
from langfuse import Langfuse

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


if __name__ == '__main__':
    trace = Langfuse().trace(
        name="一次trace",
        user_id="001",
    )
    print(trace.id)

    input = 'sora是什么时候发布的？'

    # 1. 创建了一个检索步骤
    span = trace.span(
        name="向量检索",
        metadata={"database": "database001"},
        input={'query': input},
        start_time=time.time()
    )

    # 模拟进行了查询并取得结果
    search_hit = ["""Since the release of ChatGPT in November 2022, the advent of AI technologies has marked a significant
transformation, reshaping interactions and integrating deeply into various facets of daily life and industry [1, 2]. Building on this momentum, OpenAI released, in February 2024, Sora, a text-to-video generative AI model that can generate videos of realistic or imaginative scenes from text prompts. Compared
to previous video generation models, Sora is distinguished by its ability to produce up to 1-minute long
videos with high quality while maintaining adherence to user’s text instructions [3]. This progression of
Sora is the embodiment of the long-standing AI research mission of equipping AI systems (or AI Agents)
with the capability of understanding and interacting with the physical world in motion. This involves developing AI models that are capable of not only interpreting complex user instructions but also applying this
understanding to solve real-world problems through dynamic and contextually rich simulations"""]
    retrieved_documents = {
        "response": search_hit
    }

    span.end(
        output=retrieved_documents,
        end_time=time.time()
    );


    # 2. 创建了一个拼接提示词步骤
    span = trace.span(
        name="拼接提示词",
        metadata={"prompt_template": "template001"},
        input={'query': input},
        start_time=time.time()
    )
    prompt = "请结合如下信息作答："+search_hit[0]+"\n 用户问题是："+input
    span.end(
        output=prompt,
        end_time=time.time()
    );

    # 3. 调用大模型步骤
    completion = openai.chat.completions.create(
        name="系统调用大模型",
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        trace_id=trace.id,
    )
    print(completion.choices[0].message.content)
    time.sleep(10)