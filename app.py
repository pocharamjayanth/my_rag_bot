import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from backend.rag_pipeline import process_and_index_pdf, retrieve_relevant_context

load_dotenv()

st.title("My RAG Bot (Vector-Backed)")

env_api_key = os.getenv("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input("Enter Gemini API Key:", value=env_api_key, type="password")

if api_key:
    genai.configure(api_key=api_key)

@st.cache_resource
def get_active_model(key: str):
    genai.configure(api_key=key)
    try:
        supported_models = [
            m.name for m in genai.list_models() 
            if "generateContent" in m.supported_generation_methods
        ]
        if "models/gemini-1.5-flash" in supported_models:
            return "models/gemini-1.5-flash"
        elif supported_models:
            return supported_models[0]
    except Exception:
        pass
    return "gemini-1.5-flash"

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file:
    os.makedirs("uploaded_files", exist_ok=True)
    temp_path = os.path.join("uploaded_files", uploaded_file.name)
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if "indexed_file" not in st.session_state or st.session_state.indexed_file != uploaded_file.name:
        with st.spinner("Chunking document and generating vector embeddings..."):
            try:
                num_chunks = process_and_index_pdf(temp_path, document_id=uploaded_file.name)
                st.session_state.indexed_file = uploaded_file.name
                st.success(f"Indexed {num_chunks} text chunks into ChromaDB!")
            except Exception as e:
                st.error(f"Indexing Error: {str(e)}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    user_query = st.text_input("Ask a question about your document:")
    if user_query:
        if not api_key:
            st.error("Please enter your Gemini API Key in the sidebar or set GEMINI_API_KEY in your .env file.")
        else:
            with st.spinner("Retrieving relevant vector context and generating response..."):
                relevant_context = retrieve_relevant_context(user_query, document_id=uploaded_file.name, top_k=3)
                
                augmented_prompt = f"""Answer the user's question using ONLY the provided context below.

Context:
{relevant_context}

Question:
{user_query}"""
                
                try:
                    selected_model = get_active_model(api_key)
                    model = genai.GenerativeModel(selected_model)
                    response = model.generate_content(augmented_prompt)
                    
                    st.markdown("### Answer")
                    st.write(response.text)
                    
                    with st.expander("View Retrieved Context Chunks"):
                        st.write(relevant_context)
                except Exception as e:
                    st.error(f"API Model Error: {str(e)}")