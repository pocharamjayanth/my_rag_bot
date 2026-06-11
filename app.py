import os
import streamlit as st
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.vectorstores import InMemoryVectorStore

# 1. Page Configuration (Clean Title - Caption Removed)
st.set_page_config(page_title="MediBot: AI Medical Assistant", page_icon="🩺", layout="wide")
st.title("🩺 MediBot: Intelligent Medical Document Assistant")

# 2. Secure API Key Interceptor
api_key = None

# Safely extract the credential string from local secrets or environment variables
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif os.environ.get("GOOGLE_API_KEY"):
    api_key = os.environ.get("GOOGLE_API_KEY")

# Intercept empty, space-only, or default placeholder strings cleanly
if not api_key or api_key.strip() == "" or api_key == "YOUR_API_KEY_HERE":
    st.error("🔑 **Gemini API Key Required**")
    st.info("""
    To activate MediBot, please ensure your valid Gemini API key is configured:
    * **Locally:** In a file named `.streamlit/secrets.toml` with the entry: `GOOGLE_API_KEY = "your_key"`
    * **Cloud Deployment:** Pasted directly into the Streamlit Cloud secrets management input box.
    """)
    st.stop()

# Set environment fallback context
os.environ["GOOGLE_API_KEY"] = api_key

# Helper function to safely read markdown behavior files
def read_markdown_file(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Load Agent identity and Skill execution workflows dynamically
agent_instructions = read_markdown_file("agent.md")
skill_instructions = read_markdown_file("skill.md")

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

# 4. Initialize RAG Pipeline (Passing api_key as a parameter breaks stale validation caches)
@st.cache_resource
def load_vector_store(runtime_key):
    if not os.path.exists("./uploaded_files") or not os.listdir("./uploaded_files"):
        return None
    
    # Load and split PDFs
    loader = DirectoryLoader('./uploaded_files', glob="./*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)
    
    # Generate vector store with the dynamically tracked runtime key argument
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=runtime_key)
    vectorstore = InMemoryVectorStore.from_documents(chunks, embeddings)
    return vectorstore

# 5. Build Database and Initialize LLM
try:
    # Trigger the pipeline passing our validated key string
    vectorstore = load_vector_store(api_key)
    if vectorstore is not None:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, google_api_key=api_key)
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

# 7. Handle User Query (Orchestrated with Agent & Skill Specifications)
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
            with st.spinner("Analyzing documents via customized agent framework..."):
                try:
                    # Retrieve relevant chunks
                    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
                    relevant_docs = retriever.invoke(user_query)
                    
                    context = "\n\n".join([doc.page_content for doc in relevant_docs])
                    
                    # Unified Contextual Architecture Blueprint
                    prompt = f"""
{agent_instructions}

{skill_instructions}

---
### RETRIEVED DOCUMENT CONTEXT:
{context}

---
### USER QUERY:
{user_query}

Remember to follow the operational constraints of the Agent and the structural layout defined in the Skill.
"""

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