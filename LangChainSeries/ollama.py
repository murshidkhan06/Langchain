from langchain_community.llms.ollama import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
##Langsmith tracking
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")


## Prompt template

prompt=ChatPromptTemplate.from_messages(
    [
        ("system","You are a helpful assistant. Please response to the user queries"),
        ("user","Question:{question}")
    ]
)

#### Streamlit framework
st.title('Langchain demo with Llama3-API')
input_text = st.text_input('Search the topic you want')

### ollama llama2 LLM
llm=Ollama(model="llama3")
output_parser = StrOutputParser

chain = prompt|llm|output_parser

if input_text:
    st.write(chain.invoke({"question":input_text}))