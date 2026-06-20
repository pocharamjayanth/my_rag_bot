import streamlit as st
import pymupdf4llm
from llama_cpp import Llama
import os

st.set_page_config(page_title="MediBot: Secure Medical RAG Assistant", layout="wide")
st.title("🩺 MediBot: Secure Offline Medical RAG Assistant")

st.sidebar.header("🧬 Architecture Configuration")
# Change this default value if your GGUF file has a different name
model_filename = st.sidebar.text_input("Local GGUF Model File Name", value="qwen2.5-7b-instruct-q4_k_m.gguf")
model_path = os.path.join(os.getcwd(), model_filename)

@st.cache_resource
def initialize_native_brain(path):
    if os.path.exists(path):
        return Llama(model_path=path, n_ctx=4096, n_threads=4)
    return None

llm = initialize_native_brain(model_path)

if llm is None:
    st.sidebar.error(f"❌ GGUF model file not detected at: {model_path}")
    st.sidebar.warning("Please verify your downloaded model weights file is sitting right inside your C:\\Users\\pocha\\RAG_Chatbot folder.")
else:
    st.sidebar.success("✅ Native C++ Inference Core Loaded Successfully!")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = ""

st.sidebar.subheader("📂 Document Ingestion Layer")
uploaded_file = st.sidebar.file_uploader("Upload Reference PDF Matrix", type=["pdf"])

if uploaded_file is not None and not st.session_state.context:
    with st.spinner("Parsing layout grids via PyMuPDF4LLM..."):
        temp_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            st.session_state.context = pymupdf4llm.to_markdown(temp_path)
            st.sidebar.success("✅ Layout Ingestion Synchronized!")
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            st.sidebar.error(f"Ingestion Exception: {e}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a medical analysis question..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if llm is None:
        st.error("Cannot process message. Local model core is not loaded.")
    else:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            full_prompt = prompt
            if st.session_state.context:
                context_snippet = st.session_state.context[:6000]
                full_prompt = f"Context:\n{context_snippet}\n\nQuestion: {prompt}\n\nAnswer explicitly using the context:"

            with st.spinner("Synthesizing context tokens..."):
                try:
                    output = llm(
                        f"<|im_start|>user\n{full_prompt}<|im_end|>\n<|im_start|>assistant\n",
                        max_tokens=512,
                        stop=["<|im_end|>", "user", "Context:"],
                        echo=False
                    )
                    response_text = output["choices"][0]["text"].strip()
                    message_placeholder.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    st.error(f"Inference processing failure: {e}")
