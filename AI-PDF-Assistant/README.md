# 📄 AI PDF Assistant

An end-to-end **Retrieval-Augmented Generation (RAG)** application that enables users to upload PDF documents and chat with them using natural language.

The application leverages **LangChain**, **ChromaDB**, **Ollama**, and **FastAPI** to retrieve relevant information from documents and generate accurate, context-aware responses through a modern custom frontend.

---

## ✨ Features

- 📂 Upload one or multiple PDF documents
- 🤖 Chat with PDFs using natural language
- 🧠 Semantic search powered by vector embeddings
- 💾 Persistent vector storage with ChromaDB
- ⚡ Local LLM inference using Ollama (Gemma 3)
- 🔍 Context-aware responses using RAG
- 🚀 FastAPI REST API backend
- 🎨 Modern HTML, CSS & JavaScript frontend
- 🗑️ Clear indexed documents and chat history

---

## 🏗️ Architecture

```text
                +----------------+
                |   Upload PDFs  |
                +--------+-------+
                         |
                         ▼
                PyMuPDF Document Loader
                         |
                         ▼
                  Text Chunking
                         |
                         ▼
         nomic-embed-text Embeddings
                         |
                         ▼
                 ChromaDB Vector Store
                         |
                  Semantic Retrieval
                         |
                         ▼
             Gemma 3 (Ollama LLM)
                         |
                         ▼
                FastAPI Backend API
                         |
                         ▼
        HTML • CSS • JavaScript Frontend
```

---

## 🛠️ Tech Stack

- Python
- FastAPI
- LangChain
- Ollama
- Gemma 3
- ChromaDB
- nomic-embed-text
- PyMuPDF
- HTML
- CSS
- JavaScript

---

## 📂 Project Structure

```text
pdf_bot/
│
├── backend/
│   ├── config.py
│   ├── llm.py
│   ├── pdf_loader.py
│   ├── vectorstore.py
│   └── server.py
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── data/
│   ├── pdfs/
│   └── chroma/
│
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/pdf_bot.git

cd pdf_bot
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Environment

**Windows**

```powershell
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 📥 Install Ollama Models

```bash
ollama pull gemma3:4b

ollama pull nomic-embed-text
```

Make sure the Ollama service is running before starting the application.

---

## ▶️ Run the Application

```bash
uvicorn backend.server:app --reload
```

Open your browser and visit:

```text
http://localhost:8000
```

---

## 📌 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/health` | Health Check |
| POST | `/api/upload` | Upload PDF documents |
| POST | `/api/chat` | Chat with indexed PDFs |
| GET | `/api/sources` | List indexed documents |
| DELETE | `/api/sources` | Clear indexed documents |

---

## 💡 How It Works

1. Upload one or more PDF documents.
2. Extract text using **PyMuPDF**.
3. Split documents into semantic chunks.
4. Generate embeddings using **nomic-embed-text**.
5. Store embeddings in **ChromaDB**.
6. Retrieve relevant chunks through semantic search.
7. Generate responses using **Gemma 3** via **Ollama**.
8. Return context-aware answers to the frontend.

---

## 🌐 Deployment

The frontend can be deployed independently using:

- Netlify
- Vercel
- GitHub Pages

The backend runs with FastAPI and can be exposed publicly using services such as **Cloudflare Tunnel** or **ngrok**.

---

## 🔮 Future Improvements

- User Authentication
- Multi-user Support
- Conversation History
- Source Citations
- Drag & Drop Uploads
- Dark Mode
- Docker Support
- Cloud Deployment

---

## 👨‍💻 Author

**ROJAL JYOTHISH**

**Machine Learning Developer**

> *Always learning, always building.* 🚀

---

## ⭐ If you found this project helpful, don't forget to give it a star!