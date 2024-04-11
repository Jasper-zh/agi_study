"""
assistants_example01 -

Author: zhang
Date: 2024/3/7
"""
from openai import OpenAI
import os
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())
# 初始化 OpenAI 服务
client = OpenAI()  # openai >= 1.3.0 起，OPENAI_API_KEY 和 OPENAI_BASE_URL 会被默认使用

import time


def wait_on_run(run, thread):
    """等待 run 结束，返回 run 对象，和成功的结果"""
    while run.status == "queued" or run.status == "in_progress":
        """还未中止"""
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id)
        print("status: " + run.status)

        # 打印调用工具的 step 详情
        if (run.status == "completed"):
            run_steps = client.beta.threads.runs.steps.list(
                thread_id=thread.id, run_id=run.id, order="asc"
            )
            for step in run_steps.data:
                if step.step_details.type == "tool_calls":
                    show_json(step.step_details)

        # 等待 1 秒
        time.sleep(1)

    if run.status == "requires_action":
        """需要调用函数"""
        # 可能有多个函数需要调用，所以用循环
        tool_outputs = []
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            # 调用函数
            name = tool_call.function.name
            print("调用函数：" + name + "()")
            print("参数：")
            print(tool_call.function.arguments)
            function_to_call = available_functions[name]
            arguments = json.loads(tool_call.function.arguments)
            result = function_to_call(arguments)
            print("结果：" + str(result))
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result),
            })

        # 提交函数调用的结果
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs,
        )

        # 递归调用，直到 run 结束
        return wait_on_run(run, thread)

    if run.status == "completed":
        """成功"""
        # 获取全部消息
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        # 最后一条消息排在第一位
        result = messages.data[0].content[0].text.value
        return run, result

    # 执行失败
    return run, None

if __name__ == '__main__':
    # 创建thread并存入元信息
    thread2 = client.beta.threads.create(
        metadata = {"fullname": "孙志岗", "username": "sunner"}
    )
    print(thread2)
    # thread3 = client.beta.threads.retrieve("thread_slZ5iJWafSwN4T346OG7aOAY")
    #client.beta.threads.update('thread_slZ5iJWafSwN4T346OG7aOAY', metadata={"uid": 990}) # 增量修改
    # res = client.beta.threads.delete("thread_slZ5iJWafSwN4T346OG7aOAY") # 删除 需要认证
    message = client.beta.threads.messages.create(
        thread_id=thread2.id,  # message 必须归属于一个 thread
        role="user",  # 取值是 user 或者 assistant。但 assistant 消息会被自动加入，我们一般不需要自己构造
        content="你都能做什么？",
    )
    #print(thread3)
    print(message)

    # assistant id 从 https://platform.openai.com/assistants 获取。你需要在自己的 OpenAI 创建一个
    assistant_id = "asst_KpC6ehe9IjPrnSFYJCiaErS8"

    run = client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=thread2.id,
    )
    print(run)
    res = wait_on_run(run, thread2)
    print(res[1])

