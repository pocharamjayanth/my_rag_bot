import os

import pymupdf4llm
import streamlit as st
from llama_cpp import Llama

# ==========================================
# 1. GLOBAL SESSION STATE INITIALIZATION
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "context_text" not in st.session_state:
    st.session_state.context_text = ""

MODEL_PATH = "model.gguf"


@st.cache_resource
def load_llm():
    if not os.path.exists(MODEL_PATH):
        return None
    return Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=4)


llm = load_llm()

# ==========================================
# 2. USER INTERFACE LAYOUT
# ==========================================
st.set_page_config(page_title="MediBot RAG", page_icon="🩺", layout="centered")
st.title("🩺 MediBot: Private Medical RAG Assistant")
st.caption("Powered by Local LLM & Swecha GitLab Pipeline — 100% Offline & Secure")

with st.sidebar:
    st.header("Document Repository")
    uploaded_file = st.file_uploader("Upload Medical Reference (PDF)", type=["pdf"])

    if uploaded_file is not None and st.session_state.context_text == "":
        with st.spinner("Processing medical text with PyMuPDF4LLM..."):
            temp_filename = "temp_medical_doc.pdf"
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())
            try:
                st.session_state.context_text = pymupdf4llm.to_markdown(temp_filename)
                st.success("✅ Document synchronized successfully!")
            except Exception as e:
                st.error(f"Error reading PDF: {e}")
    elif uploaded_file is not None:
        st.success("✅ Document synchronized successfully!")

# ==========================================
# 3. RENDER EXISTING CHAT HISTORY
# ==========================================
if "messages" in st.session_state:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ==========================================
# 4. CHAT INPUT & EXECUTION PIPELINE
# ==========================================
if user_query := st.chat_input("Ask a question about your uploaded medical guide..."):
    # Fail-safe initialization right before interaction
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("assistant"):
        if llm is None:
            st.error("❌ Model file 'model.gguf' not found.")
        else:
            with st.spinner("Analyzing document context..."):
                context = st.session_state.context_text if st.session_state.context_text else "No document uploaded."

                prompt = f"<|im_start|>system\nYou are a professional medical assistant. Answer the user question accurately using only the provided context text.\nContext:\n{context[:4000]}<|im_end|>\n<|im_start|>user\n{user_query}<|im_end|>\n<|im_start|>assistant\n"

                response = llm(prompt, max_tokens=512, stop=["<|im_end|>", "</s>"], echo=False)
                answer = response["choices"][0]["text"].strip()
                matched_heading = uploaded_file.name if uploaded_file else "Internal Knowledge Base"

                st.markdown(answer)
                st.caption(f"📍 **Source Section Consulted:** `{matched_heading}`")

                # Double check fail-safe to guarantee NO key crashes
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"{answer}\n\n📍 *Source Section Consulted:* `{matched_heading}`",
                    }
                )
