import chromadb
from chromadb import Settings
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from pdfminer.high_level import extract_pages # 提取每页
from pdfminer.layout import LTTextContainer


# 加载当前目录下的.env到系统环境
_ = load_dotenv(find_dotenv())
# 配置 OpenAI 服务 （从系统环境读取）
client = OpenAI()

prompt_template = """
你是一个问答机器人。
你的任务是根据下述给定的已知信息回答用户问题。
确保你的回复完全依据下述已知信息。不要编造答案。

已知信息:
__INFO__

用户问：
__QUERY__

请用中文回答用户问题。
"""


class MyVectorDBConnector:
    def __init__(self, collection_name, embedding_fn):
        chroma_client = chromadb.Client(Settings(allow_reset=True))

        # 为了演示，实际不需要每次 reset()
        chroma_client.reset()

        # 创建一个 collection
        self.collection = chroma_client.get_or_create_collection(name=collection_name)
        self.embedding_fn = embedding_fn

    def add_documents(self, documents):
        '''向 collection 中添加文档与向量'''
        self.collection.add(
            embeddings=self.embedding_fn(documents),  # 每个文档的向量
            documents=documents,  # 文档的原文
            ids=[f"id{i}" for i in range(len(documents))]  # 每个文档的 id
        )

    def search(self, query, top_n):
        '''检索向量数据库'''
        results = self.collection.query(
            query_embeddings=self.embedding_fn([query]),
            n_results=top_n
        )
        return results

# 拼接提示词
def build_prompt(prompt_template, user_input, known_info):
    '''将 Prompt 模板赋值'''
    prompt = prompt_template
    prompt = prompt.replace("__INFO__", known_info)
    prompt = prompt.replace("__QUERY__", user_input)
    return prompt


# 大模型响应
def get_completion(prompt, model="gpt-3.5-turbo"):
    '''封装 openai 接口'''
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content

def get_embeddings(texts, model="text-embedding-ada-002"):
    '''封装 OpenAI 的 Embedding 模型接口'''
    data = client.embeddings.create(input=texts, model=model).data
    return [x.embedding for x in data]


def extract_text_from_pdf(filename, page_numbers=None, min_line_length=1):
    '''从 PDF 文件中（按指定页码）提取文字'''
    paragraphs = []
    buffer = ''
    full_text = ''
    # 遍历每页
    for i, page_layout in enumerate(extract_pages(filename)):
        # 如果指定了页码列表[1,4,5]，就只查看指定的页
        if page_numbers is not None and i not in page_numbers:
            continue
        # 遍历改页的元素
        for element in page_layout:
            # 如果元素是文本类型，则进行拼接
            if isinstance(element, LTTextContainer):
                full_text += element.get_text() + '\n'

    # 按空行分隔，获得文本列表
    lines = full_text.split('\n')
    for text in lines:
        # 忽略标题
        if len(text) >= min_line_length:
            # 将当前行拼接到缓冲区，如果此行结尾有'-'说明单词一部分被写到下行了，现在直接去掉
            buffer += (' '+text) if not text.endswith('-') else text.strip('-')
        elif buffer:
            paragraphs.append(buffer)
            buffer = ''
    if buffer:
        paragraphs.append(buffer)
    return paragraphs


if __name__ == '__main__':
    user_input = 'sora是啥时候发布的呀'

    db = MyVectorDBConnector("test",get_embeddings)
    paragraphs = extract_text_from_pdf("2402.17177.pdf")
    # client.embeddings.create这个接口一次嵌入不能太多，这里取段落列表的前15段内容。
    db.add_documents(paragraphs[:15])
    res = db.search('sora是啥时候发布的呀',2)

    # 用户问题结合检索结果构成提示词
    prompt = build_prompt(prompt_template, user_input, str(res))
    print("提示词："+prompt)
    res = get_completion(prompt)
    print("GPT-3.5回复：\n" + res)