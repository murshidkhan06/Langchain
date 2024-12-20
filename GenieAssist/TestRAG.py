import streamlit as st
import os
import PyPDF2
import openai
import numpy as np
import faiss
import uuid
from typing import List, Tuple

# Initialize Azure OpenAI
openai.api_type = "azure"
openai.api_key = "YOUR_AZURE_OPENAI_API_KEY"
openai.api_base = "https://YOUR_AZURE_ENDPOINT.openai.azure.com"
openai.api_version = "2023-05-15"

# Initialize FAISS index
embedding_dim = 1536  # Dimensionality of the OpenAI embeddings
if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = faiss.IndexFlatL2(embedding_dim)
    st.session_state.doc_metadata = {}  # Stores metadata for documents
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []  # Maintain chat history

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to embed text using Azure OpenAI
def embed_text(text: str):
    response = openai.Embedding.create(
        input=text,
        engine="text-embedding-ada-002"
    )
    return np.array(response['data'][0]['embedding'], dtype="float32")

# Function to chunk large text into smaller segments
def chunk_text(text: str, max_tokens: int = 500):
    words = text.split()
    for i in range(0, len(words), max_tokens):
        yield " ".join(words[i:i + max_tokens])

# Function to add documents to FAISS
def add_documents_to_faiss(documents: List[dict]):
    for doc in documents:
        chunks = list(chunk_text(doc['content']))
        for chunk in chunks:
            embedding = embed_text(chunk)
            st.session_state.faiss_index.add(np.array([embedding]))
            doc_id = str(uuid.uuid4())
            st.session_state.doc_metadata[doc_id] = {"chunk": chunk, "metadata": doc["metadata"]}

# Function to perform RAG-based retrieval
def retrieve_context(query: str) -> List[str]:
    # Embed the query
    query_embedding = embed_text(query)

    # Retrieve top-k similar documents
    k = 5
    distances, indices = st.session_state.faiss_index.search(np.array([query_embedding]), k)

    # Collect relevant chunks
    retrieved_chunks = []
    for idx in indices[0]:
        if idx != -1:  # -1 indicates no match
            for doc_id, metadata in st.session_state.doc_metadata.items():
                if np.allclose(embed_text(metadata["chunk"]), st.session_state.faiss_index.reconstruct(idx)):
                    retrieved_chunks.append(metadata["chunk"])
    return retrieved_chunks

# Function to generate a response with conversation context
def generate_response(query: str) -> str:
    # Retrieve context
    retrieved_chunks = retrieve_context(query)
    document_context = "\n\n".join(retrieved_chunks)

    # Build conversation context
    conversation_history = "\n".join([f"User: {q}\nAssistant: {r}" for q, r in st.session_state.conversation_history])
    prompt = f"""
The following is a conversation with a user about documents. Use the document context and conversation history to provide accurate answers.

Document Context:
{document_context}

Conversation History:
{conversation_history}

User: {query}
Assistant:"""

    # Generate response
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=prompt,
        max_tokens=300
    )
    return response.choices[0].text.strip()

# Streamlit UI
st.title("Chat with Your Documents (FAISS)")
st.sidebar.header("Upload PDFs")

# Upload PDFs in the sidebar
uploaded_files = st.sidebar.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

# Process uploaded files
if uploaded_files:
    documents = []
    for file in uploaded_files:
        pdf_text = extract_text_from_pdf(file)
        documents.append({
            "id": file.name,
            "content": pdf_text,
            "metadata": {"filename": file.name}
        })

    # Add documents to FAISS
    add_documents_to_faiss(documents)
    st.sidebar.success(f"Added {len(uploaded_files)} documents to the vector store!")

# Chat UI
st.header("Chat with Your Documents")
user_query = st.text_input("Enter your question:")

if user_query:
    # Generate a response
    answer = generate_response(user_query)

    # Update conversation history
    st.session_state.conversation_history.append((user_query, answer))

    # Display the conversation
    for query, response in st.session_state.conversation_history:
        st.write(f"**User**: {query}")
        st.write(f"**Assistant**: {response}")
