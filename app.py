import os
import re
import streamlit as st
import pymupdf4llm
from llama_cpp import Llama

# 1. Page Configuration
st.set_page_config(page_title="MediBot: Local Assistant", page_icon="🩺", layout="wide")
st.title("🩺 MediBot: Local-First Intelligent Document Assistant")
st.caption("Powered by Mozilla.ai Roaming RAG Blueprint (100% Private, Offline)")

# Ensure storage directories exist
os.makedirs("./uploaded_files", exist_ok=True)

# Update this path if your model filename is slightly different
MODEL_PATH = "./models/Qwen2.5-7B-Instruct-Q4_K_M.gguf" 

# 2. Lazy Initialization of Local Model Engine
@st.cache_resource
def get_local_llm(model_path):
    if not os.path.exists(model_path):
        st.error(f"❌ Model file not found at `{model_path}`. Please verify your models folder.")
        st.stop()
    # n_ctx sets the token context capacity for local data evaluation
    return Llama(model_path=model_path, n_ctx=4096, n_threads=4)

try:
    llm = get_local_llm(MODEL_PATH)
except Exception as e:
    st.error(f"Failed to initialize local inference engine: {e}")
    st.stop()

# Helper function to segment Markdown by header levels
def partition_markdown_to_sections(md_text):
    pattern = r'(^#{1,4}\s+.*$)'
    parts = re.split(pattern, md_text, flags=re.MULTILINE)
    
    sections = {}
    current_heading = "Introduction / Document Meta"
    sections[current_heading] = ""
    
    for part in parts:
        if re.match(pattern, part):
            current_heading = part.strip()
            sections[current_heading] = ""
        else:
            sections[current_heading] += part
            
    return {k: v.strip() for k, v in sections.items() if v.strip()}

# 3. Sidebar Document Processing Matrix
with st.sidebar:
    st.header("📂 Document Ingestion")
    uploaded_file = st.file_uploader("Upload structured PDF Guide", type="pdf")
    
    if uploaded_file:
        file_save_path = os.path.join("./uploaded_files", uploaded_file.name)
        with open(file_save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        with st.spinner("Extracting layout headers via PyMuPDF4LLM..."):
            raw_markdown = pymupdf4llm.to_markdown(file_save_path)
            document_sections = partition_markdown_to_sections(raw_markdown)
            
        st.success("Document structured cleanly!")
        st.info(f"Detected {len(document_sections)} unique content headers.")
    else:
        document_sections = None
        st.info("Upload a medical guide or textbook chapter to begin.")

# 4. Chat Interface Management
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Mozilla Blueprint Workflow Execution
if user_query := st.chat_input("Ask a question about the document..."):
    if not document_sections:
        st.warning("Please upload a PDF document in the sidebar first.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Locating relevant document section (Phase 1: FIND)..."):
                headers_list = "\n".join([f"- {h}" for h in document_sections.keys()])
                
                routing_prompt = f"""<|im_start|>system
You are an expert document index router. Analyze the user's question and choose exactly ONE section heading from the provided index list that contains the answer. Return only the exact heading string.
List of Available Headings:
{headers_list}
<|im_end|>
<|im_start|>user
Question: {user_query}
Target Heading:<|im_end|>"""

                routing_response = llm(routing_prompt, max_tokens=60, temperature=0.0)
                selected_heading = routing_response["choices"][0]["text"].strip()
                
                matched_heading = None
                for heading in document_sections.keys():
                    if heading in selected_heading or selected_heading in heading:
                        matched_heading = heading
                        break
                if not matched_heading:
                    matched_heading = list(document_sections.keys())[0]

            with st.spinner(f"Synthesizing answer from [{matched_heading}] (Phase 2: ANSWER)..."):
                context_text = document_sections[matched_heading]
                
                generation_prompt = f"""<|im_start|>system
You are a precise assistant. Synthesize a clean answer using ONLY the provided text context.
Context Section [{matched_heading}]:
{context_text}
<|im_end|>
<|im_start|>user
Question: {user_query}
Answer:<|im_end|>"""

                generation_response = llm(generation_prompt, max_tokens=512, temperature=0.2)
                answer = generation_response["choices"][0]["text"].strip()
                
            st.markdown(answer)
            st.caption(f"📍 **Source Section Consulted:** `{matched_heading}`")
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"{answer}\n\n📍 *Source Section Consulted:* `{matched_heading}`"
            })