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
    try:
        collection.delete(where={"document_id": document_id})
    except Exception:
        pass

    try:
        full_text = pymupdf4llm.to_markdown(pdf_path)
        if not full_text.strip():
            raise ValueError("Extracted document text is empty.")

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
    except Exception as e:
        raise RuntimeError(f"Failed to process and index PDF: {str(e)}")

def retrieve_relevant_context(query: str, document_id: str, top_k: int = 3) -> str:
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={"document_id": document_id}
    )
    if results and "documents" in results and len(results["documents"]) > 0:
        retrieved_chunks = results["documents"][0]
        return "\n\n---\n\n".join(retrieved_chunks)
    return ""