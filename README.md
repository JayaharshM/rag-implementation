# Local RAG Backend Architecture

This repository contains the backend for a fully functional Retrieval-Augmented Generation (RAG) system built with FastAPI, PyMuPDF, ChromaDB, and a remote Ollama LLM setup. 

## Key Features

1. **Intelligent PDF Extraction**: Extracts raw text dynamically from uploaded PDF documents using `PyMuPDF`.
2. **Pure Python Chunking Engine**: A customized logic-based chunker that splits document text into precise 500-word semantic chunks, guaranteeing a 50-word overlap for high context retention without relying on external tokenization libraries.
3. **Remote Embeddings Integration**: Generates vector representations of document chunks dynamically by sending them to a remote Ollama server running the `nomic-embed-text` embedding model.
4. **Isolated Vector Storage**: Safely persists vectors locally using `ChromaDB`, filtering all search queries strictly by a specific `user_id` to ensure absolute context isolation and security across user documents.
5. **Streaming Generative AI**: Passes the retrieved user-specific context to a remote Ollama server running the `qwen2.5:3b` LLM, streaming the answer back token-by-token (Server-Sent Events) via FastAPI's `StreamingResponse`.
6. **Built-in HTML Client**: A fully functional, responsive vanilla JS web interface for testing PDF uploads and streaming real-time chat conversations.

---

## Folder Structure

```text
backend/
├── requirements.txt            # Python dependencies
├── README.md                   # This documentation
├── index.html                  # Built-in chat testing web interface
├── uploads/                    # Local temporary storage for uploaded PDFs
├── chroma_db/                  # Persistent SQLite database for vector embeddings
└── app/
    ├── main.py                 # FastAPI application, CORS setup, and API routes
    └── services/
        ├── document_processor.py # PDF text extraction logic (PyMuPDF)
        ├── chunker.py            # 500-word / 50-overlap sliding window logic
        ├── vector_store.py       # ChromaDB persistence, user filtering, & remote embedding
        └── llm.py                # HTTP Client streaming requests to remote Ollama LLM
```

---

## Environment Variables

The backend relies on a remote Ollama cluster for embeddings and generation. If you change your infrastructure, adjust the environment variables accordingly. 

By default, the backend falls back to the following configurations:

- `OLLAMA_BASE_URL`: `http://192.168.1.40:11434`
- `OLLAMA_EMBED_MODEL`: `nomic-embed-text`
- `OLLAMA_LLM_MODEL`: `qwen2.5:3b`

*Note: Ensure your remote Ollama instance is configured to accept connections from your machine by adjusting the `OLLAMA_HOST` variable on the server if needed.*

---

## API Endpoints

### 1. `POST /upload`
**Purpose**: Ingests a PDF document into the RAG system.
**Payload**: `multipart/form-data`
- `file`: The PDF document.
- `user_id`: A string representing the owner of the document.
**Process**: Saves the file -> Extracts text -> Runs the Chunker -> Calls remote embeddings -> Inserts to ChromaDB mapped to `user_id`.
**Example**:
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.pdf;type=application/pdf" \
  -F "user_id=user_123"
```

### 2. `POST /query`
**Purpose**: For testing retrieval logic without LLM generation.
**Payload**: `application/json`
- `user_id`: The ID of the document owner.
- `message`: The search query.
**Process**: Embeds the message -> Queries ChromaDB using `where={"user_id": ...}` -> Returns top 5 relevant text chunks.
**Example**:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "What is the secret password?"}'
```

### 3. `POST /chat`
**Purpose**: The main Chat completion endpoint for the frontend UI.
**Payload**: `application/json`
- `user_id`: The ID of the document owner.
- `message`: The prompt to ask the AI.
**Process**: Performs the same retrieval as `/query`, bundles the chunks into an augmented prompt, passes it to Ollama LLM via `POST /api/generate`, and yields a `text/event-stream` stream to the frontend.
**Example**:
```bash
curl -N -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "What is the secret password?"}'
```

---

## Getting Started

### 1. Environment Setup

Ensure you are inside the `backend/` directory, then create and activate a Python virtual environment:

```bash
# Create Virtual Environment
python3 -m venv venv

# Activate Virtual Environment (macOS/Linux)
source venv/bin/activate
```

### 2. Install Dependencies

Install all the required Python packages (FastAPI, Uvicorn, PyMuPDF, ChromaDB, etc.):

```bash
pip install -r requirements.txt
```

### 3. Run the Server

Start the FastAPI application. The `--reload` flag ensures hot-reloading during active development.

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test with the UI

Because we have CORS enabled, you don't even need a separate frontend server to test the system. Simply open `index.html` in your web browser:
1. Double-click `index.html` from your file explorer.
2. Enter a user ID.
3. Upload a PDF.
4. Begin chatting with your documents!
