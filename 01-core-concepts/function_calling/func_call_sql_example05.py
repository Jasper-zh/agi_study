"""
func_call_sql_example05.py -

Author: zhang
Date: 2024/2/2
"""

from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = OpenAI()

def get_sql_completion(messages, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        tools=[{  # 摘自 OpenAI 官方示例 https://github.com/openai/openai-cookbook/blob/main/examples/How_to_call_functions_with_chat_models.ipynb
            "type": "function",
            "function": {
                "name": "ask_database",
                "description": "根据用户的数据库查询问题，输出满足条件sql输出",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": f"""
                            根据用户信息提取生成SQL查询的语句
                            SQL需要使用的表结构如下:
                            {database_schema_string}
                            SQL查询需要满足MySQL的语法
                            """,
                        }
                    },
                    "required": ["query"],
                }
            }
        }],
    )
    return response.choices[0].message

if __name__ == '__main__':
    #  描述数据库表结构
    database_schema_string = """
    CREATE TABLE customers (
        id INT PRIMARY KEY NOT NULL, -- 主键，不允许为空
        customer_name VARCHAR(255) NOT NULL, -- 客户名，不允许为空
        email VARCHAR(255) UNIQUE, -- 邮箱，唯一
        register_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 注册时间，默认为当前时间
    );
    CREATE TABLE products (
        id INT PRIMARY KEY NOT NULL, -- 主键，不允许为空
        product_name VARCHAR(255) NOT NULL, -- 产品名称，不允许为空
        price DECIMAL(10,2) NOT NULL -- 价格，不允许为空
    );
    CREATE TABLE orders (
        id INT PRIMARY KEY NOT NULL, -- 主键，不允许为空
        customer_id INT NOT NULL, -- 客户ID，不允许为空
        product_id INT NOT NULL, -- 产品ID，不允许为空
        price DECIMAL(10,2) NOT NULL, -- 价格，不允许为空
        status INT NOT NULL, -- 订单状态，整数类型，不允许为空。0代表待支付，1代表已支付，2代表已退款
        create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间，默认为当前时间
        pay_time TIMESTAMP -- 支付时间，可以为空
    );
    """

    prompt = "统计每月每件商品的销售额"
    prompt = "消费最高的用户是谁？"
    # prompt = "这星期消费最高的用户是谁？他买了哪些商品？ 每件商品买了几件？花费多少？"
    messages = [
        {"role": "system", "content": "基于 order 表回答用户问题"},
        {"role": "user", "content": prompt}
    ]
    response = get_sql_completion(messages)
    print(response.tool_calls[0].function.arguments)