import streamlit as st
import pymupdf4llm
from llama_cpp import Llama
import os

# ==========================================
# 1. CONFIGURATION (Change your model file name here if needed)
# ==========================================
MODEL_PATH = "model.gguf"  # Make sure your 4.7GB model is named exactly this or update it here

# ==========================================
# 2. STREAMLIT SESSION STATE INITIALIZATION
# ==========================================
# This fixes the "AttributeError: st.session_state has no attribute 'messages'" crash
if "messages" not in st.session_state:
    st.session_state.messages = []

if "context_text" not in st.session_state:
    st.session_state.context_text = ""

# ==========================================
# 3. CACHED RESOURCE LOADERS
# ==========================================
@st.cache_resource
def load_llm():
    """Loads the heavy local GGUF model into memory once."""
    if not os.path.exists(MODEL_PATH):
        st.error(f"❌ Model file not found at '{MODEL_PATH}'. Please ensure your 4.7GB model file is in the project folder.")
        return None
    return Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=4)

llm = load_llm()

# ==========================================
# 4. USER INTERFACE LAYOUT
# ==========================================
st.set_page_config(page_title="MediBot RAG", page_icon="🩺", layout="centered")
st.title("🩺 MediBot: Private Medical RAG Assistant")
st.caption("Powered by Local LLM & Swecha GitLab Pipeline — 100% Offline & Secure")

# Sidebar for PDF document uploads
with st.sidebar:
    st.header("Document Repository")
    uploaded_file = st.file_uploader("Upload Medical Reference (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("Processing medical text with PyMuPDF4LLM..."):
            # Save the uploaded stream to a temporary local file
            temp_filename = "temp_medical_doc.pdf"
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Extract high-quality Markdown text chunks from the PDF
            try:
                extracted_md = pymupdf4llm.to_markdown(temp_filename)
                st.session_state.context_text = extracted_md
                st.success("✅ Document synchronized successfully!")
            except Exception as e:
                st.error(f"Error reading PDF: {e}")

# ==========================================
# 5. RENDER EXISTING CHAT HISTORY
# ==========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 6. CHAT INPUT & EXECUTION PIPELINE
# ==========================================
if user_query := st.chat_input("Ask a question about your uploaded medical guide..."):
    
    # 1. Display and save user query
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
        
    # 2. Process query using AI Engine
    with st.chat_message("assistant"):
        if llm is None:
            st.warning("AI Engine is offline. Please resolve the model file missing error.")
        else:
            with st.spinner("Analyzing document context..."):
                # Pull the extracted document text for context
                context = st.session_state.context_text if st.session_state.context_text else "No document uploaded."
                
                # Format a precise system prompt for the offline model
                prompt = f"""[INST] You are a professional medical assistant. Answer the user question accurately using only the provided context text. If you don't know, say you don't know.
                
                Context:
                {context[:4000]} 
                
                Question: {user_query} [/INST]"""
                
                # Execute text generation
                response = llm(prompt, max_tokens=512, stop=["[/INST]", "</s>"], echo=False)
                answer = response["choices"][0]["text"].strip()
                
                # Set dynamic reference tags
                matched_heading = uploaded_file.name if uploaded_file else "Internal Knowledge Base"
                
                # Render components instantly onto the screen
                st.markdown(answer)
                st.caption(f"📍 **Source Section Consulted:** `{matched_heading}`")
                
                # Save assistant response cleanly to historical session state arrays
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"{answer}\n\n📍 *Source Section Consulted:* `{matched_heading}`"
                })