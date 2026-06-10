import os
import streamlit as st
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

# 1. Page Configuration
st.set_page_config(page_title="MediBot: AI Medical Assistant", page_icon="🩺", layout="wide")
st.title("🩺 MediBot: Intelligent Medical Document Assistant")
st.caption("A RAG-powered hackathon application built by Jayanth & Harsha")

# 2. Setup API Key - Insert your AI Studio key here
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE"

# Ensure upload directory exists
os.makedirs("./uploaded_files", exist_ok=True)

# 3. Sidebar for Dynamic File Upload
with st.sidebar:
    st.header("📂 Document Ingestion")
    uploaded_files = st.file_uploader("Upload Medical Guidelines / PDFs", accept_multiple_files=True, type="pdf")
    
    if uploaded_files:
        # Save uploaded files to the local directory
        for uploaded_file in uploaded_files:
            with open(os.path.join("./uploaded_files", uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"{len(uploaded_files)} PDF(s) uploaded successfully!")
    else:
        st.info("Please upload one or more PDFs to start chatting.")

# 4. Initialize RAG Pipeline (Cached to avoid reloading on every keystroke)
@st.cache_resource
def load_vector_store():
    if not os.path.exists("./uploaded_files") or not os.listdir("./uploaded_files"):
        return None
    
    # Load and split PDFs
    loader = DirectoryLoader('./uploaded_files', glob="./*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)
    
    # Generate vector store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = Chroma.from_documents(chunks, embeddings)
    return vectorstore

# 5. Build Database and Initialize LLM
try:
    vectorstore = load_vector_store()
    if vectorstore is not None:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
        db_ready = True
    else:
        db_ready = False
except Exception as e:
    st.error(f"Error building vector store: {e}")
    db_ready = False

# 6. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 View Source References"):
                st.markdown(message["sources"])

# 7. Handle User Query
if user_query := st.chat_input("Ask a question about the uploaded documents..."):
    if not db_ready:
        st.warning("Database is not ready. Please upload PDF documents in the sidebar first.")
    else:
        # Append and display user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing documents and generating medical insights..."):
                try:
                    # Retrieve relevant chunks
                    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
                    relevant_docs = retriever.invoke(user_query)
                    
                    context = "\n\n".join([doc.page_content for doc in relevant_docs])
                    
                    # Prompt Engineering ensuring grounding
                    prompt = f"""You are MediBot, an expert AI medical assistant. Answer the query based strictly and only on the provided context.
If the answer cannot be found in the context, state clearly: "I cannot find the answer in the provided documents." Do not make up information.

Context:
{context}

Query:
{user_query}"""

                    response = llm.invoke(prompt)
                    answer = response.content
                    
                    # Format sources for UI expander
                    source_text = ""
                    for i, doc in enumerate(relevant_docs):
                        source_text += f"**Source {i+1} (Page {doc.metadata.get('page', 'N/A')}):**\n`{doc.page_content[:300]}...`\n\n"

                except Exception as e:
                    answer = f"Error processing request: {e}"
                    source_text = ""
                
                st.markdown(answer)
                if source_text:
                    with st.expander("📚 View Source References"):
                        st.markdown(source_text)
        
        # Save assistant response and sources to session state
        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": source_text})