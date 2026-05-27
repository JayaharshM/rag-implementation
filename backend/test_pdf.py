import fitz
from app.services.document_processor import DocumentProcessor
import os

def create_sample_pdf(file_path):
    doc = fitz.open()
    page = doc.new_page()
    
    # Insert some test text
    text = "Hello, this is a sample PDF document for testing the extractor.\nIt contains multiple lines of text.\n\nLet's see if PyMuPDF can extract it correctly!"
    page.insert_text((50, 50), text, fontsize=12)
    
    doc.save(file_path)
    doc.close()
    print(f"Created sample PDF at {file_path}")

def test_pdf_extractor():
    sample_pdf_path = "sample_test.pdf"
    
    try:
        # Create a sample PDF first
        create_sample_pdf(sample_pdf_path)
        
        # Test the processor
        print("\n--- Testing DocumentProcessor.process_pdf ---")
        processor = DocumentProcessor()
        results = processor.process_pdf(sample_pdf_path)
        
        print(f"Extracted {len(results)} pages.")
        for page_data in results:
            print(f"\nPage {page_data['page']}:")
            print("-" * 20)
            print(page_data['text'])
            print("-" * 20)
            
    finally:
        # Clean up
        if os.path.exists(sample_pdf_path):
            os.remove(sample_pdf_path)
            print(f"\nCleaned up {sample_pdf_path}")

if __name__ == "__main__":
    test_pdf_extractor()
