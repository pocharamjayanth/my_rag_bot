import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from backend.rag_pipeline import process_and_index_pdf, retrieve_relevant_context

load_dotenv()

st.title("My RAG Bot (Vector-Backed)")

# Sidebar API Key configuration
env_api_key = os.getenv("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input("Enter Gemini API Key:", value=env_api_key, type="password")

if api_key:
    genai.configure(api_key=api_key)

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file:
    os.makedirs("uploaded_files", exist_ok=True)
    temp_path = f"uploaded_files/{uploaded_file.name}"
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if "indexed_file" not in st.session_state or st.session_state.indexed_file != uploaded_file.name:
        with st.spinner("Chunking document and generating vector embeddings..."):
            num_chunks = process_and_index_pdf(temp_path, document_id=uploaded_file.name)
            st.session_state.indexed_file = uploaded_file.name
            st.success(f"Indexed {num_chunks} text chunks into ChromaDB!")

    user_query = st.text_input("Ask a question about your document:")
    if user_query:
        if not api_key:
            st.error("Please enter your Gemini API Key in the sidebar or set GEMINI_API_KEY in your .env file.")
        else:
            with st.spinner("Retrieving relevant vector context and generating response..."):
                relevant_context = retrieve_relevant_context(user_query, top_k=3)
                
                augmented_prompt = f"""
                Answer the user's question using ONLY the provided context below.

                Context:
                {relevant_context}

                Question:
                {user_query}
                """
                
                try:
                    # Dynamically get models supported for text generation
                    supported_models = [
                        m.name for m in genai.list_models() 
                        if 'generateContent' in m.supported_generation_methods
                    ]
                    
                    # Choose gemini-1.5-flash or the first available model
                    target_model = "models/gemini-1.5-flash"
                    if target_model not in supported_models and supported_models:
                        target_model = supported_models[0]
                    
                    model = genai.GenerativeModel(target_model)
                    response = model.generate_content(augmented_prompt)
                    
                    st.markdown("### Answer")
                    st.write(response.text)
                    
                    with st.expander("View Retrieved Context Chunks"):
                        st.write(relevant_context)
                except Exception as e:
                    st.error(f"API Model Error: {str(e)}")
