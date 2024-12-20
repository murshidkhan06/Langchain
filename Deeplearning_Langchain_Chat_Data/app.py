import os
import openai
import sys
from langchain.document_loaders import PyPDFLoader

### Document loading from Web
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import OpenAIWhisperParser
from langchain.document_loaders.blob_loaders.youtube_audio import YoutubeAudioLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter, TokenTextSplitter


openai.api_key  = os.environ['OPENAI_API_KEY']
loader = PyPDFLoader("Test.pdf")
pages = loader.load()
len(pages)
page = pages[0]
print(page.page_content[0:500])
print(page.metadata)

chunk_size =26
chunk_overlap = 4

r_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap
)
c_splitter = CharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap
)

text1 = 'abcdefghijklmnopqrstuvwxyz'
r_splitter.split_text(text1)

text2 = 'abcdefghijklmnopqrstuvwxyzabcdefg'
print(r_splitter.split_text(text2))

text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=1000,
    chunk_overlap=150,
    length_function=len
)

docs = text_splitter.split_documents(pages)

print(len(docs))

text_splitter = TokenTextSplitter(chunk_size=1, chunk_overlap=0)

text1 = "foo bar bazzyfoo"

print(text_splitter.split_text(text1))

text_splitter = TokenTextSplitter(chunk_size=10, chunk_overlap=0)

docs = text_splitter.split_documents(pages)

print(docs[0])