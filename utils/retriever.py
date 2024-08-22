import os
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

load_dotenv()
os.environ['GROQ_KEY'] = os.getenv('GROQ_KEY')

# LLaMa3
llm = ChatGroq(api_key=os.environ['GROQ_KEY'], model = 'llama3-8b-8192', temperature=0.5)
# BGE embedding model 
embedding = HuggingFaceEmbeddings(model_name = 'BAAI/bge-large-en-v1.5')

# prompt_template
prompt_template = ChatPromptTemplate.from_template(
    """
    You are a financial assistant AI bot that generates responses to queries based on provided financial reports. Answer the following question strictly based on the given context. Do not add any additional information or context.

    Format your output as follows:
    <format>{format}</format> \n\n
    <context>{context}</context>
    Question: {input}
    """
)

def load_documents(FILE_PATH : str):
    print("path: ",FILE_PATH)
    loader = PyPDFLoader(FILE_PATH)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size = 4500, chunk_overlap = 200)
    documents = splitter.split_documents(documents=documents)
    return documents


def rag_model(file_path : str): 
    global prompt_template, llm, embedding
    documents = load_documents(FILE_PATH=file_path)
    vectorstore = Chroma.from_documents(documents, embedding)
    retriever = vectorstore.as_retriever(search_kwargs = {'k' : 6})
    compressor = LLMChainExtractor.from_llm(llm)
    compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)
    document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt_template)
    rag = create_retrieval_chain(compression_retriever, document_chain)

    return rag

def get_information(prompt : str, file_path : str, update_type : str):
    financial_result_output = """
    Company : 
    Total Income/ Revenue : 
    Profit before Tax :
    Profit after Tax : 
    """

    order_result_output = """
    Company: 
    Order received from (if mentioned): 
    Order amount: 
    Execution period of order: 
    """
    if update_type == "Result" : 
        outputFormat = financial_result_output
    else: 
        outputFormat = order_result_output
    rag = rag_model(file_path)
    response = rag.invoke({'format' : outputFormat, 'input' : prompt})
    return response['answer']


# print(get_information('What is the Total Revenue/Income, Profit before and after tax in the current quarter and the last qaurter of the same year of the company? Give consolidated results.', '../sample2.pdf', 'Result'))
