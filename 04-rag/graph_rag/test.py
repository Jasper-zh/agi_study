from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),base_url=os.getenv("BASE_URL"))
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role":"user","content":"你好啊"}
    ]
)
print(response.choices[0].message.content)
print(client.models.list().data)