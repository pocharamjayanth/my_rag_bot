import os
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pymupdf4llm

chroma_client = chromadb.PersistentClient(path="./chroma_db")

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="document_chunks",
    embedding_function=embedding_fn
)

def process_and_index_pdf(pdf_path: str, document_id: str) -> int:
    """Extracts text, splits into chunks, creates embeddings, and stores in ChromaDB."""
    full_text = pymupdf4llm.to_markdown(pdf_path)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_text(full_text)
    
    ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
    
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )
    return len(chunks)

def retrieve_relevant_context(query: str, top_k: int = 3) -> str:
    """Performs semantic vector search and returns top matching chunks."""
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    if results and "documents" in results and len(results["documents"]) > 0:
        retrieved_chunks = results["documents"][0]
        return "\n\n---\n\n".join(retrieved_chunks)
    return ""
