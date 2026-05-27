from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.document_processor import DocumentProcessor
from app.services.chunker import TextChunker
from app.services.vector_store import VectorStore
from app.services.llm import LLMClient
import os
import uuid
import shutil

app = FastAPI(title="RAG Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services globally so they are loaded once
print("Initializing services...")
vector_store = VectorStore(persist_directory="./chroma_db")
processor = DocumentProcessor()
chunker = TextChunker(chunk_size=500, overlap=50)
llm_client = LLMClient()

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are currently supported")

    # 1. Receive file & Save to disk
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Extract text
        extracted_data = processor.process_pdf(file_path)
        if not extracted_data:
            raise HTTPException(status_code=500, detail="Failed to extract text from PDF")
            
        # 3. Chunk
        chunks = chunker.chunk_extracted_data(extracted_data)
        if not chunks:
            raise HTTPException(status_code=500, detail="No chunks generated from the document")
            
        # 4 & 5. Embed & Store in ChromaDB
        embeddings = vector_store.embedder.encode(chunks)
        
        metadatas = [
            {"user_id": user_id, "file_id": file_id, "filename": file.filename}
            for _ in chunks
        ]
        chunk_ids = [f"{file_id}_chunk_{i}" for i in range(len(chunks))]
        
        vector_store.add_chunks(
            chunks=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=chunk_ids
        )
        
        return {
            "message": "File processed and stored successfully",
            "file_id": file_id,
            "filename": file.filename,
            "chunks_processed": len(chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
class QueryRequest(BaseModel):
    user_id: str
    message: str

@app.post("/query")
async def query_documents(request: QueryRequest):
    try:
        # Search ChromaDB for top-5 similar chunks
        results = vector_store.search(
            query=request.message,
            user_id=request.user_id,
            top_k=5
        )
        
        # Extract the chunks from ChromaDB's response format
        context_chunks = []
        if results and results.get('documents') and len(results['documents']) > 0:
            context_chunks = results['documents'][0]
            
        return {
            "context": context_chunks,
            "message": "Successfully retrieved context",
            "results_count": len(context_chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    try:
        # 1. Retrieve context
        results = vector_store.search(
            query=request.message,
            user_id=request.user_id,
            top_k=5
        )
        
        context_chunks = []
        if results and results.get('documents') and len(results['documents']) > 0:
            context_chunks = results['documents'][0]
            
        # 2. Construct the augmented prompt
        context_str = "\n\n".join(context_chunks)
        prompt = (
            "You are a helpful AI assistant. Use the following retrieved context to answer the user's question.\n"
            "If the answer is not contained in the context, say so.\n\n"
            f"Context:\n{context_str}\n\n"
            f"Question: {request.message}\n\n"
            "Answer:"
        )
        
        # 3. Stream the response directly to the client
        return StreamingResponse(
            llm_client.generate_stream(prompt), 
            media_type="text/event-stream"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
