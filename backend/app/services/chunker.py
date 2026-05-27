class TextChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initializes the chunker.
        Since this is pure Python without a tokenizer like tiktoken, 
        we approximate tokens using words (splitting by whitespace).
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_extracted_data(self, extracted_data: list[dict]) -> list[str]:
        """
        Takes the output from the PDF/DOCX extractor and chunks it.
        """
        # Combine all text from all pages
        full_text = " ".join([page_data.get("text", "") for page_data in extracted_data])
        return self.chunk_text(full_text)

    def chunk_text(self, text: str) -> list[str]:
        """
        Chunks text into roughly `chunk_size` tokens (words) with `overlap` tokens overlap.
        """
        words = text.split()
        chunks = []
        
        if not words:
            return chunks

        start_idx = 0
        while start_idx < len(words):
            end_idx = start_idx + self.chunk_size
            chunk_words = words[start_idx:end_idx]
            
            chunk_text = " ".join(chunk_words).strip()
            if chunk_text:  # Ensure no empty or malformed chunks
                chunks.append(chunk_text)
                
            # Move forward by chunk_size minus overlap
            start_idx += (self.chunk_size - self.overlap)
            
        return chunks
