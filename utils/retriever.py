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
# from langchain_core.messages import HumanMessage

load_dotenv()
os.environ['GROQ_KEY'] = os.getenv('GROQ_KEY')

# LLaMa3
llm = ChatGroq(api_key=os.environ['GROQ_KEY'], model = 'llama3-8b-8192', temperature=0.7)
# BGE embedding model 
embedding = HuggingFaceEmbeddings(model_name = 'BAAI/bge-large-en-v1.5')

# prompt_template
prompt_template = ChatPromptTemplate.from_template(
    """
    You are a financial assistant that generates responses to queries based on financial reports.
    Aanswer the following question based on only the given context. \
    Don't prepend or postpend any information on your own and just answer what has been asked. \
    
    Output should be in the format given below : 
    {format}
    If something isnt retrievable, leave it blank.
    <context> {context} </context>
    Question : {input}
    """
)

def ask_question(question : str):
    question_template = f"Answer with either yes or no. Analyze the question properly and answer. {question}"
    # print(question_template)
    response = llm.invoke(question_template)
    return response.content

def load_documents(FILE_PATH : str):
    loader = PyPDFLoader(FILE_PATH)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size = 5000, chunk_overlap = 300)
    documents = splitter.split_documents(documents=documents)
    return documents


def rag_model(file_path : str): 
    global prompt_template, llm, embedding
    documents = load_documents(FILE_PATH=file_path)
    vectorstore = Chroma.from_documents(documents, embedding)
    retriever = vectorstore.as_retriever(search_kwargs = {'k' : 6})
    document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt_template)
    rag = create_retrieval_chain(retriever, document_chain)
    return rag

def get_information(prompt : str, file_path : str):
    financial_result_output = """
    ###
    Company : 
    Total Income/ Revenue : 
    Total Profit before Tax :
    Total Profit after Tax : 
    ###
    """

    order_result_output = """
    ### 
    Company name : 
    Order received from (if mentioned) : 
    Order amount : 
    Execution period of order : 
    ###
    """
    rag = rag_model(file_path)
    response = rag.invoke({'format' : financial_result_output, 'input' : prompt})
    return response['answer']


# print(get_information("What is the amount of order received by the company? What is the execution period / deadline in months to complete the order? By whom was the order given? Give the amount using the symbol 'Rs.'.", 'D:\\bse-orderly\\bajel_order.pdf'))
print(get_information("What is the Total Income/Revenue that the company made? What is it's Proft/Loss before and after tax? Don't give the amount inside brackets, rather use this symbol - 'Rs.' . Give the results for only the latest quarter. What is the company name? Give standalone quarter end results", 'D:\\bse-orderly\\sample3.pdf'))