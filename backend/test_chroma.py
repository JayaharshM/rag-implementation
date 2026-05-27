from app.services.vector_store import VectorStore
import uuid
import os
import shutil

def test_chroma():
    # Clean up previous db if exists to start fresh for test
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
        
    print("Initializing VectorStore (this loads ChromaDB and the Embedder)...")
    store = VectorStore(persist_directory="./chroma_db")
    
    # 1. Prepare sample chunks and generate embeddings
    chunks = [
        "The quick brown fox jumps over the lazy dog.", # user1
        "Python is a versatile programming language.", # user2
        "A fast brown fox leaped over a sleepy hound.", # user1 (semantically similar to chunk 1)
        "Data science and machine learning rely heavily on Python." # user2 (semantically similar to chunk 2)
    ]
    
    print("Generating embeddings for chunks...")
    embeddings = store.embedder.encode(chunks).tolist()
    
    # 2. Metadata and IDs
    metadatas = [
        {"user_id": "user1", "file_id": "file_A", "filename": "story.pdf"},
        {"user_id": "user2", "file_id": "file_B", "filename": "code.pdf"},
        {"user_id": "user1", "file_id": "file_A", "filename": "story.pdf"},
        {"user_id": "user2", "file_id": "file_B", "filename": "code.pdf"}
    ]
    ids = [str(uuid.uuid4()) for _ in range(4)]
    
    # 3. Add to ChromaDB
    print("Inserting chunks into ChromaDB...")
    store.add_chunks(chunks=chunks, embeddings=embeddings, metadatas=metadatas, ids=ids)
    print("Insertion complete.")
    
    # 4. Test querying with user_id filtering
    print("\n--- Testing Query ---")
    query_text = "Tell me about a jumping fox."
    print(f"Query: '{query_text}'")
    
    print("\nQuerying as 'user1' (Expects to find the fox sentences):")
    results_user1 = store.search(query=query_text, user_id="user1", top_k=2)
    
    if results_user1['documents'] and len(results_user1['documents'][0]) > 0:
        for i, (doc, meta) in enumerate(zip(results_user1['documents'][0], results_user1['metadatas'][0])):
            print(f"  Result {i+1}: '{doc}' | user_id: {meta['user_id']} | file: {meta['filename']}")
    else:
        print("  No results found.")
        
    print("\nQuerying as 'user2' (Expects NOT to find the fox sentences, even if semantically similar):")
    results_user2 = store.search(query=query_text, user_id="user2", top_k=2)
    
    if results_user2['documents'] and len(results_user2['documents'][0]) > 0:
        for i, (doc, meta) in enumerate(zip(results_user2['documents'][0], results_user2['metadatas'][0])):
            print(f"  Result {i+1}: '{doc}' | user_id: {meta['user_id']} | file: {meta['filename']}")
    else:
        print("  No results found.")
        
if __name__ == "__main__":
    test_chroma()
