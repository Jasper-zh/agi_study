from langchain.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())

# 加载pdf 取第一页内容
loader = PyPDFLoader("2402.17177.pdf")
pages = loader.load_and_split()
print(pages[0].page_content)

# langchain的段落分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=100,  # 思考：为什么要做overlap
    length_function=len,
    add_start_index=True,
)

# 分割器去分割第一页内容
paragraphs = text_splitter.create_documents([pages[0].page_content])


if __name__ == '__main__':
    # 灌库
    embeddings = OpenAIEmbeddings() # 词嵌入器
    db = Chroma.from_documents(paragraphs, embeddings) # 存入向量数据库：传入段落列表和词嵌入器（向量化方式）


    # Prompt模板
    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 获取大模型
    llm = ChatOpenAI(temperature=0)  # 发散性为0
    # 获取搜索器
    retriever = db.as_retriever(search_kwargs={"k": 1})  # 检索结果只取一个
    # 构建链式调用器（参数question运行时输入，context为检索结果）
    rag_chain = (
            {"question": RunnablePassthrough(), "context": retriever} # 参数是检索器时会进行调用，拿结果再构建提示词
            | prompt
            | llm
            | StrOutputParser()
    )

    res = rag_chain.invoke("sora是什么时候发布的")
    print(res)