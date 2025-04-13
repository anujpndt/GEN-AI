import os 
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings 
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain.chains.combine_documents import create_stuff_documents_chain 
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain 
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader 

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
groq_api_key=os.getenv("GROQ_API_KEY")

llm=ChatGroq(groq_api_key=groq_api_key,model_name="Llama3-8b-8192")

prompt=ChatPromptTemplate.from_messages(
    """Answer the following question based on the provided context only.
    Please provide the most accurate response based on the question
    <context>
    {context}
    <context>
    
    Question:{input}
        
    """

)

def create_embedding():
    if "vectors" not in st.session_state:
        st.session_state.embeddings=OpenAIEmbeddings()
        st.session_state.loader=PyPDFDirectoryLoader("research paper")
        st.session_state.docs=st.session_state.loader_load()
        st.session_state.text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
        st.session_state.final_documents=st.session_state.text_splitter.split_documents(st.session_state.docs[:50])
        st.session_state.vector=FAISS.from_documents(st.session_state.final_documents,st.session_state.embeddings)
        

user_prompt=st.text_input("Enter your Query from research paper")

if st.button("Documents embedding"):
    create_embedding()
    
    st.write("vector store is ready")
    
import time 

if user_prompt:
    document_chain=create_stuff_documents_chain(llm,prompt)  
    retriever=st.session_state.vector.as_retriever()
    retrieval_chain=create_retrieval_chain(retriever,document_chain)
    
    
    start=time.process_time()
    response=retrieval_chain.invoke({'input':user_prompt})
    print(f"Response time:{time.process_time()-start}")
    
    
    st.write(response['answer'])
    
    
    #with streamlit expander
    with st.expander("Document Similarity Search_"):
        for i,doc in enumerate(response['content']):
            st.write(doc.page_content)
            st.write("------------")
            
    
    
    

    