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

# 加载并分页
loader = PyPDFLoader("2402.17177.pdf")
pages = loader.load_and_split()
print(pages[0].page_content)

# 段落分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=100,  # 思考：为什么要做overlap
    length_function=len,
    add_start_index=True,
)

# 分段
paragraphs = text_splitter.create_documents([pages[0].page_content])


if __name__ == '__main__':
    # 灌库
    embeddings = OpenAIEmbeddings()
    db = Chroma.from_documents(paragraphs, embeddings)


    # Prompt模板
    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # Chain
    llm = ChatOpenAI(temperature=0)
    retriever = db.as_retriever(search_kwargs={"k": 1})
    rag_chain = (
            {"question": RunnablePassthrough(), "context": retriever}
            | prompt
            | llm
            | StrOutputParser()
    )

    res = rag_chain.invoke("sora是什么时候发布的")
    print(res)