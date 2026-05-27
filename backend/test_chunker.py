from app.services.document_processor import DocumentProcessor
from app.services.chunker import TextChunker
import fitz
import os

def create_long_pdf(file_path):
    doc = fitz.open()
    
    # We want a long text to test chunks. 
    # Let's generate about 2000 words, split across multiple pages.
    words = [f"word_{i}" for i in range(1, 2001)]
    
    # Insert 500 words per page
    for p in range(4):
        page_words = words[p*500:(p+1)*500]
        long_text = " ".join(page_words)
        
        page = doc.new_page()
        rect = fitz.Rect(50, 50, 550, 800)
        page.insert_textbox(rect, long_text, fontsize=10)
    
    doc.save(file_path)
    doc.close()
    print(f"Created long sample PDF at {file_path}")

def test_chunker():
    pdf_path = "long_sample.pdf"
    try:
        create_long_pdf(pdf_path)
        
        processor = DocumentProcessor()
        extracted_data = processor.process_pdf(pdf_path)
        
        chunker = TextChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk_extracted_data(extracted_data)
        
        print(f"\n--- Testing TextChunker ---")
        print(f"Total extracted pages: {len(extracted_data)}")
        print(f"Total text length (words): {len(extracted_data[0]['text'].split())}")
        print(f"Total chunks created: {len(chunks)}\n")
        
        for i, chunk in enumerate(chunks):
            chunk_words = chunk.split()
            print(f"Chunk {i + 1}:")
            print(f"  Word count: {len(chunk_words)}")
            print(f"  Starts with: '{chunk_words[0]} ...'")
            print(f"  Ends with: '... {chunk_words[-1]}'")
            
            if i > 0:
                # verify overlap
                prev_chunk_words = chunks[i-1].split()
                # The last 50 words of previous chunk should be the first 50 words of this chunk
                expected_overlap = prev_chunk_words[-50:]
                actual_overlap = chunk_words[:50]
                if expected_overlap == actual_overlap:
                    print("  [SUCCESS] 50-word overlap matches previous chunk!")
                else:
                    print("  [ERROR] Overlap mismatch!")
            
            if not chunk:
                print("  [ERROR] Chunk is empty!")
            print("-" * 30)
            
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f"\nCleaned up {pdf_path}")

if __name__ == "__main__":
    test_chunker()
