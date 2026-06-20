# 🩺 MediBot: Private & Secure Medical RAG Assistant

An enterprise-grade, 100% offline Retrieval-Augmented Generation (RAG) system engineered to parse complex medical literature and provide secure, locally-synthesized insights without external cloud API dependencies.

## 🧠 The Core Problem & Solution
* **The Problem:** Uploading sensitive medical documents or patient records to public cloud LLM APIs introduces severe data privacy risks, data leaks, and violates compliance frameworks.
* **The Solution:** MediBot retains data entirely within the host machine's local hardware boundary. By combining an ultra-fast markdown document parser with a local quantized LLM engine, data processing remains completely private and offline.

## 🛠️ Technical Architecture & Stack
| Layer | Technology Used | Purpose & Design Choice |
| :--- | :--- | :--- |
| **Frontend UI** | Streamlit | Lightweight, reactive chat interface and sidebar document repository. |
| **Document Ingestion** | PyMuPDF4LLM | Converts raw multi-page PDFs into structured Markdown to preserve text and table hierarchies. |
| **Inference Engine** | Llama-cpp-python | High-performance, quantized C++ backend binding for local LLM execution. |
| **Foundational Brain** | Qwen-2.5-7B-Instruct (GGUF) | A 7-billion parameter state-of-the-art model quantized to 4-bit precision (~4.7 GB size) optimized for complex reasoning. |

## 🚀 Local Execution Pipeline
1. **Document Ingest:** The user uploads a medical PDF guide through the Streamlit interface.
2. **Context Parsing:** PyMuPDF4LLM extracts text into clean Markdown strings, preserving layout definitions without stripping headings.
3. **State Management:** Session memory tracks conversation threads using st.session_state to prevent data loss across Streamlit's structural execution re-runs.
4. **Local Inference:** The quantized Qwen model reads context chunks directly from system RAM, streaming an offline response with strict source tracking parameters.