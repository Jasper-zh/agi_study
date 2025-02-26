from langchain.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

loader = PyPDFLoader("2402.17177.pdf")
pages = loader.load_and_split()
print(pages[0].page_content)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=100,  # 思考：为什么要做overlap
    length_function=len,
    add_start_index=True,
)

paragraphs = text_splitter.create_documents([pages[0].page_content])

for para in paragraphs:
    print(para.page_content)
    print('-------')


if __name__ == '__main__':
    # 灌库
    embeddings = OpenAIEmbeddings()
    db = Chroma.from_documents(paragraphs, embeddings)

    # LangChain内置的 RAG 实现
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0),
        retriever=db.as_retriever()
    )

    query = "sora什么时候发布的呀"
    response = qa_chain.invoke(query)
    print(response["result"])