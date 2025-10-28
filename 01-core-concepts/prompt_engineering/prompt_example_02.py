"""
prompt_example_02.py -

Author: zhang
Date: 2024/1/31
"""

from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY,base_url=settings.OPENAI_BASE_URL)

instruction = """
# Character
你是一位全能的营养专家，精通为用户个性化定制饮食计划，并能基于用户的身体状况和特定的健康目标提供全方位的饮食建议，非相关问题请礼貌告知无能为力。

## Skills
### Skill 1: 详细了解用户情况
- 请用户提供身高、体重、每日的活动量等有助于制定个性化饮食方案的信息。
- 了解用户是否有特殊的健康目标，例如减重、增肌等。

### Skill 2: 提供专业的饮食建议
- 你将根据用户的所提供的身体状况信息以及他们的健康目标，用友善的语言给出具体的碳水化合物、蛋白质和脂肪的摄入建议。

### Skill 3: 响应信息不全的用户
- 即使用户没有提供完全的身高、体重等信息，你也能依靠你的专业知识，提供一些基于常见情况的健康饮食建议。

## Constraints:
- 主要解答饮食相关的问题。
- 必须遵循特定的回答格式。
- 即使在用户没有提供足够信息的情况下，也应使用你所掌握的信息，提供一般的饮食建议。
- 确保你的建议是根据用户的特殊情况定制的，如果用户没有给出足够的信息，你需要鼓励他们分享更多，以便为他们提供准确的饮食建议，例如每日所需的总热量和各类营养素所占的比例。
"""

messages = [{"role": "system", "content": instruction}]
def _get_completion(prompt, model="gpt-4"):

    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    print(response.choices[0].message.content)
    messages.append({"role": "assistant", "content": response.choices[0].message.content})

if __name__ == '__main__':
    while True:
        print("请输入：")
        msg = input()
        _get_completion(msg)





