import json
from langfuse import Langfuse
from langfuse.model import CreateDatasetRequest, CreateDatasetItemRequest
from tqdm import tqdm


# # 调整数据格式 {"input":{...},"expected_output":"label"}
# data = []
# with open('my_annotations.jsonl', 'r', encoding='utf-8') as fp:
#     for line in fp:
#         example = json.loads(line.strip())
#         item = {
#             "input": {
#                 "outlines": example["outlines"],
#                 "user_input": example["user_input"]
#             },
#             "expected_output": example["label"]
#         }
#         data.append(item)


from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
def add_data():
    # 加载文件数据比如json、excel，得到构建成自己自定义的提示词格式
    data = [
        {
          "input": {
              "user": "你好，我无法登录我的账户，我忘记了密码。"
          },
          "output": {
              "user": "抱歉听到您遇到了问题。您可以尝试通过“忘记密码”选项重置您的密码。"
          },
        },
        {
          "input": {
              "user": "我试过了，但是我无法收到重置密码的电子邮件。"
          },
          "output": "很抱歉给您带来不便。请提供您的账户邮箱地址，我会查看一下。",
        },
        {
          "input": {
              "user": "我的邮箱是example@example.com。"
          },
          "output": "感谢您的提供。我将立即查看您的账户并发送一封重置密码的邮件给您。",
        },
        {
          "input": {
              "user": "好的，谢谢你的帮助。"
          },
          "output": "不客气，请耐心等待您的邮件，并尽快重新设置密码。如果您需要进一步的帮助，请随时联系我们。",
        }
      ]

    # init
    langfuse = Langfuse()

    # 考虑演示运行速度，只上传前50条数据
    for item in tqdm(data):
        langfuse.create_dataset_item(
            dataset_name="mydata",
            input=item["input"],
            expected_output=item["output"]
        )

langfuse = Langfuse()

def simple_evaluation(output, expected_output):
    return output == expected_output

def run_evaluation(chain, dataset_name, run_name):
    dataset = langfuse.get_dataset(dataset_name)

    def process_item(item):
        handler = item.get_langchain_handler(run_name=run_name)

        # Assuming chain.invoke is a synchronous function
        output = chain.invoke(item.input, config={"callbacks": [handler]})

        # Assuming handler.root_span.score is a synchronous function
        handler.root_span.score(
            name="accuracy",
            value=simple_evaluation(output, item.expected_output)
        )
        print('.', end='', flush=True)

    for item in dataset.items:
        process_item(item)


from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

need_answer = PromptTemplate.from_template("""
*********
你是一个客服根据用户问题，给出解决措施。
*********
学员输入:
{user}
*********
不要回答无关内容""")

model = ChatOpenAI(temperature=0, model_kwargs={"seed": 42})
parser = StrOutputParser()

chain_v1 = (
        need_answer
        | model
        | parser
)

if __name__ == '__main__':
    run_evaluation(chain_v1, "mydata", "001")

