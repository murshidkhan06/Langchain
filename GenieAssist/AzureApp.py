from dotenv import load_dotenv
import streamlit as st
import os
import tiktoken
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from langchain.llms import AzureOpenAI


os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"
os.environ["OPENAI_API_BASE"] = "https://rs-nec-openai-scus.openai.azure.com/"
os.environ["OPENAI_API_KEY"] = ""

def main():
    #load_dotenv()
    print("main created")
    st.set_page_config(page_title="Ask your Genie")
    st.header("Ask your Genie 💬")

    # upload file
    pdf = st.file_uploader("Upload your PDF", type="pdf")

    # extract the text
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # split into chunkspip ins
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        # create embeddings
        #embeddings = OpenAIEmbeddings()
        embeddings = OpenAIEmbeddings(openai_api_key="",
                         deployment="nec-text-embedding-ada-002",
                         model="text-embedding-ada-002",
                         openai_api_base="https://rs-nec-openai-scus.openai.azure.com/"
                         , openai_api_type="azure",chunk_size = 1)
        print("Embedding created")
        knowledge_base = FAISS.from_texts(chunks, embeddings)
        print("knowledge_base created")
        # show user input
        user_question = st.text_input("Ask a question about your PDF:")
        if user_question:
            docs = knowledge_base.similarity_search(user_question)

            #llm = OpenAI()
            llm = AzureOpenAI(deployment_name="nec-chat-model-35turbo", model_name="gpt-35-turbo")
            print(llm)
            chain = load_qa_chain(llm, chain_type="stuff")
            print("Chain created")
            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=user_question)
                print(cb)

            st.write(response)


if __name__ == '__main__':
    main()