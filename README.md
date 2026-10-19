# My RAG Bot 🤖 Vector-Backed Document Q&A System

A local Retrieval-Augmented Generation (RAG) web application built with **Streamlit**, **ChromaDB**, **Sentence-Transformers**, and **Google Gemini API**. 

Unlike naive context-stuffing applications, **My RAG Bot** extracts document text, recursively splits it into semantic chunks, generates vector embeddings locally, indexes them in a persistent ChromaDB database, and performs top-k similarity retrieval to provide accurate, grounded answers via Gemini.

---

## 👥 Contributors & Team

This project was developed through collaborative contribution by:

* **Jayanth** — Core RAG Pipeline, Vector Indexing (ChromaDB) & Gemini Integration
* **Krishna** — Data Extraction (\PyMuPDF4LLM\) & Document Preprocessing
* **Gargeya** — UI/UX Design & Streamlit Interactive Application Logic
* **Srujan** — System Testing, Environment Configuration & Optimization

---

## 🚀 Key Features

* **Local Vector Database**: Efficient, persistent vector storage using **ChromaDB** (\./chroma_db\).
* **Semantic Text Chunking**: Intelligent recursive splitting using \RecursiveCharacterTextSplitter\ (500 char size, 50 char overlap).
* **Local Embeddings**: High-density semantic vector generation via \ll-MiniLM-L6-v2\ (\sentence-transformers\).
* **Dynamic Model Resolution**: Automatically detects active Gemini models (\genai.list_models()\) to eliminate endpoint version conflicts.
* **Streamlit UI**: Simple file upload, question input, and collapsible views to inspect retrieved context chunks in real time.

---

## 🏗️ Architecture Flow

1. **PDF Processing**: Uploaded PDF is converted to structured markdown via \pymupdf4llm\.
2. **Text Chunking**: Document is segmented into overlapping semantic chunks.
3. **Embedding Generation**: Local embedding function converts chunks into numerical vector representations.
4. **ChromaDB Indexing**: Chunks and metadata are stored in local persistent storage.
5. **Vector Retrieval**: User query is vectorized to retrieve top-3 most relevant context blocks.
6. **Augmented Generation**: Gemini generates an exact answer conditioned strictly on retrieved context.

---

## 🛠️ Installation & Local Setup

### 1. Prerequisites
* Python 3.10 or higher
* Git

### 2. Clone the Repository
\\\ash
git clone https://github.com/pocharamjayanth/my_rag_bot.git
cd my_rag_bot
\\\

### 3. Create & Activate Virtual Environment
**Windows (PowerShell):**
\\\powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
\\\

**Linux / macOS:**
\\\ash
python3 -m venv venv
source venv/bin/activate
\\\

### 4. Install Dependencies
\\\ash
pip install streamlit chromadb sentence-transformers langchain-text-splitters pymupdf4llm google-generativeai python-dotenv torchvision
\\\

---

## ⚙️ Configuration & Execution

### Environment Variables
Create a \.env\ file in the root directory (or use the sidebar password input in Streamlit):
\\\env
GEMINI_API_KEY=your_gemini_api_key_here
\\\

### Run Application
Launch Streamlit bound strictly to \localhost\:
\\\ash
python -m streamlit run app.py --server.address=127.0.0.1
\\\
Open **\http://127.0.0.1:8501\** in your browser.

---

## 📂 Project Structure

\\\	ext
my_rag_bot/
├── backend/
│   └── rag_pipeline.py     # Chunking, local embeddings, and ChromaDB retrieval logic
├── uploaded_files/          # Temporary local PDF staging
├── chroma_db/               # Persistent local vector database directory
├── app.py                   # Streamlit frontend & augmented generation
├── .env                     # Private environment variables (API keys)
├── .gitignore               # Ignored database files, env, and virtualenvs
└── README.md                # Project documentation
\\\

---

## 📝 License
This project is open-source and available under the **MIT License**.
