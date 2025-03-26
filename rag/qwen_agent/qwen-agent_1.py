import pprint
import urllib.parse
import json5
import logging
import io
import sys
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool


# 创建一个自定义的日志处理器来捕获日志输出
class LogCapture:
    def __init__(self):
        self.log_capture_string = io.StringIO()
        self.log_handler = logging.StreamHandler(self.log_capture_string)
        self.log_handler.setLevel(logging.INFO)
        self.log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(self.log_formatter)

        # 获取 qwen_agent 的日志记录器
        self.logger = logging.getLogger('qwen_agent_logger')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.log_handler)

        # 也可以捕获根日志记录器的输出
        self.root_logger = logging.getLogger()
        self.root_logger.setLevel(logging.INFO)
        self.root_logger.addHandler(self.log_handler)

    def get_log(self):
        return self.log_capture_string.getvalue()

    def clear_log(self):
        self.log_capture_string.truncate(0)
        self.log_capture_string.seek(0)


# 初始化日志捕获器
log_capture = LogCapture()


# 步骤 1（可选）：添加一个名为 `my_image_gen` 的自定义工具。
@register_tool('my_image_gen')
class MyImageGen(BaseTool):
    # `description` 用于告诉智能体该工具的功能。
    description = 'AI 绘画（图像生成）服务，输入文本描述，返回基于文本信息绘制的图像 URL。'
    # `parameters` 告诉智能体该工具有哪些输入参数。
    parameters = [{
        'name': 'prompt',
        'type': 'string',
        'description': '期望的图像内容的详细描述',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        # `params` 是由 LLM 智能体生成的参数。
        prompt = json5.loads(params)['prompt']
        prompt = urllib.parse.quote(prompt)
        return json5.dumps(
            {'image_url': f'https://image.pollinations.ai/prompt/{prompt}'},
            ensure_ascii=False)


# 步骤 2：配置您所使用的 LLM。
llm_cfg = {
    # 使用 DashScope 提供的模型服务：
    'model': 'qwen-max',
    'model_server': 'dashscope',
    'api_key': '',
    'generate_cfg': {
        'top_p': 0.8
    }
}

# 步骤 3：创建一个智能体。这里我们以 `Assistant` 智能体为例，它能够使用工具并读取文件。
system_instruction = '''你是一个乐于助人的AI助手。
在收到用户的请求后，你应该：
- 首先绘制一幅图像，得到图像的url，
- 然后运行代码`request.get`以下载该图像的url，
- 最后从给定的文档中选择一个图像操作进行图像处理。
用 `plt.show()` 展示图像。
你总是用中文回复用户。'''
tools = ['my_image_gen', 'code_interpreter']  # `code_interpreter` 是框架自带的工具，用于执行代码。
files = ['./docs/1-平安商业综合责任保险（亚马逊）.txt']  # 给智能体一个 PDF 文件阅读。

# 清除之前的日志
log_capture.clear_log()

# 创建智能体
bot = Assistant(llm=llm_cfg,
                system_message=system_instruction,
                function_list=tools,
                files=files)

# 步骤 4：作为聊天机器人运行智能体。
messages = []  # 这里储存聊天历史。
query = "有哪些保险啊？"
# 将用户请求添加到聊天历史。
messages.append({'role': 'user', 'content': query})
response = []
current_index = 0

# 运行智能体
for response in bot.run(messages=messages):
    # 在第一次响应时，分析日志以查找召回的文档内容
    if current_index == 0:
        # 获取日志内容
        log_content = log_capture.get_log()

        print("\n===== 从日志中提取的检索信息 =====")
        # 查找与检索相关的日志行
        retrieval_logs = [line for line in log_content.split('\n')
                          if any(keyword in line.lower() for keyword in
                                 ['retriev', 'search', 'chunk', 'document', 'ref', 'token'])]

        # 打印检索相关的日志
        for log_line in retrieval_logs:
            print(log_line)

        # 尝试从日志中提取文档内容
        # 通常在日志中会有类似 "retrieved document: ..." 或 "content: ..." 的行
        content_logs = [line for line in log_content.split('\n')
                        if any(keyword in line.lower() for keyword in
                               ['content', 'text', 'document', 'chunk'])]

        print("\n===== 可能包含文档内容的日志 =====")
        for log_line in content_logs:
            print(log_line)

        print("===========================\n")

    current_response = response[0]['content'][current_index:]
    current_index = len(response[0]['content'])
    print(current_response, end='')

# 将机器人的回应添加到聊天历史。
messages.extend(response)

# 运行结束后，分析完整的日志
print("\n\n===== 运行结束后的完整日志分析 =====")
log_content = log_capture.get_log()

# 尝试从日志中提取更多信息
print("\n1. 关键词提取:")
keyword_logs = [line for line in log_content.split('\n') if 'keywords' in line.lower()]
for log_line in keyword_logs:
    print(log_line)

print("\n2. 文档处理:")
doc_logs = [line for line in log_content.split('\n') if 'doc' in line.lower() or 'chunk' in line.lower()]
for log_line in doc_logs:
    print(log_line)

print("\n3. 检索相关:")
retrieval_logs = [line for line in log_content.split('\n') if
                  'retriev' in line.lower() or 'search' in line.lower() or 'ref' in line.lower()]
for log_line in retrieval_logs:
    print(log_line)

print("\n4. 可能包含文档内容的日志:")
content_logs = [line for line in log_content.split('\n') if 'content:' in line.lower() or 'text:' in line.lower()]
for log_line in content_logs:
    print(log_line)

print("===========================\n")