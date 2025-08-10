import requests
import json
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())
# 初始化 OpenAI 服务
client = OpenAI()  # openai >= 1.3.0 起，OPENAI_API_KEY 和 OPENAI_BASE_URL 会被默认使用

import time


def running(run, thread):
    """等待 run 结束，返回 run 对象，和成功的结果"""
    while run.status == "queued" or run.status == "in_progress":
        """还未中止，再查一次获取最新run信息"""
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id)
        print("status: " + run.status)

        # 现在如果完成了则获取下所有步骤
        if (run.status == "completed"):
            run_steps = client.beta.threads.runs.steps.list(
                thread_id=thread.id, run_id=run.id, order="asc"
            )
            print(run_steps.data)
            for i,step in enumerate(run_steps.data):
                # if step.step_details.type == "tool_calls":
                    print(f"步骤:{i+1}")
                    print(step.step_details)

        # 等待 1 秒
        time.sleep(1)


    if run.status == "requires_action":
        """状态为需要调用函数"""
        # 可能有多个函数需要调用，所以用循环
        tool_outputs = []
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            # 调用函数
            name = tool_call.function.name
            if name not in ["get_adcode", "get_weather"]:
                break
            print("调用函数：" + name + "()")
            print("参数：" + tool_call.function.arguments)
            function_to_call = globals().get(name)
            arguments = json.loads(tool_call.function.arguments)
            result = function_to_call(arguments)
            print("函数结果：" + str(result))
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result),
            })

        # 提交函数调用的结果
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs)

        time.sleep(1)
        return running(run, thread)

    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        result = messages.data[0].content[0].text.value
        return run, result


    # 执行失败
    return run, None


if __name__ == '__main__':
    # 创建thread
    thread = client.beta.threads.create(
        metadata= {"uid": 29, "username": "zhangsan", "age": 18}
    )
    print(thread)

    # 创建一个消息在thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,  # message 必须归属于一个 thread
        role="user",  # assistant回复的消息会自动加入到thread，一般只需要创建user的消息进去即可
        content="鸡和兔在一个笼子里，共有35个头，94只脚，那么鸡有多少只，兔有多少只？",
    )
    print(message)

    # assistant id 从 https://platform.openai.com/assistants 获取。你需要在自己的 OpenAI 创建一个
    assistant_id = "asst_KpC6ehe9IjPrnSFYJCiaErS8"

    # 创建一次run
    run = client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=thread.id,
    )
    print(run)

    # 对当前run进行监控
    res = running(run,thread)
    print(res[1])
