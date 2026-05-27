import chromadb
import requests
import os

class OllamaEmbedder:
    def __init__(self):
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://192.168.1.40:11434")
        self.model = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")

    def encode(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        url = f"{self.base_url}/api/embeddings"
        for text in texts:
            response = requests.post(url, json={
                "model": self.model,
                "prompt": text
            })
            response.raise_for_status()
            embeddings.append(response.json()["embedding"])
        return embeddings

class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection("documents")
        self.embedder = OllamaEmbedder()

    def add_chunks(self, chunks: list[str], embeddings: list[list[float]], metadatas: list[dict], ids: list[str]):
        """
        Adds chunks, their vectors, and metadata to ChromaDB.
        metadatas should contain: user_id, file_id, filename
        """
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query: str, user_id: str, top_k: int = 5):
        """
        Searches ChromaDB for the most relevant chunks, filtered by user_id.
        """
        # Generate embedding for the query
        query_embedding = self.embedder.encode([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            where={"user_id": user_id}  # Filtering by user_id
        )
        return results
