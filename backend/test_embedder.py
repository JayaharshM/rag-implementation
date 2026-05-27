from sentence_transformers import SentenceTransformer

def test_embedder():
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    # Load the model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Simulate chunks from the TextChunker
    chunks = [
        "This is the first chunk of text from the document.",
        "Here is a second chunk that contains some different information.",
        "And a third chunk just to be absolutely sure the embeddings work."
    ]
    
    print(f"Embedding {len(chunks)} chunks...")
    
    # Generate embeddings
    embeddings = model.encode(chunks)
    
    # Verify the output
    print(f"\n--- Embedding Results ---")
    print(f"Number of embeddings returned: {len(embeddings)}")
    
    for i, embedding in enumerate(embeddings):
        # Convert to list of floats if it's a numpy array
        emb_list = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
        
        print(f"\nChunk {i + 1}: '{chunks[i]}'")
        print(f"Vector length (dimensions): {len(emb_list)}")
        print(f"Vector type: {type(emb_list)}")
        print(f"First 5 floats: {emb_list[:5]}")
        print(f"Last 5 floats: {emb_list[-5:]}")
        
if __name__ == "__main__":
    test_embedder()
