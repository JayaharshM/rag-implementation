from fastapi.testclient import TestClient
from app.main import app, vector_store
import fitz
import os

client = TestClient(app)

def create_sample_pdf(file_path):
    doc = fitz.open()
    page = doc.new_page()
    text = "This is a real test document for the end-to-end API pipeline.\n" * 50
    rect = fitz.Rect(50, 50, 550, 800)
    page.insert_textbox(rect, text, fontsize=10)
    doc.save(file_path)
    doc.close()

def test_upload_endpoint():
    pdf_path = "e2e_test.pdf"
    try:
        print("Creating a real test PDF...")
        create_sample_pdf(pdf_path)
        
        print("\nSending POST request to /upload API endpoint...")
        with open(pdf_path, "rb") as f:
            response = client.post(
                "/upload",
                files={"file": ("e2e_test.pdf", f, "application/pdf")},
                data={"user_id": "test_user_e2e"}
            )
            
        print(f"Status Code: {response.status_code}")
        print(f"Response JSON: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ API End-to-End Pipeline Successful!")
            # Verify data is in Chroma
            print("Verifying data in VectorStore...")
            results = vector_store.search("test document end-to-end", user_id="test_user_e2e", top_k=1)
            
            if results['documents'] and len(results['documents'][0]) > 0:
                print("✅ Found document successfully via query!")
                print(f"Document snippet: '{results['documents'][0][0][:100]}...'")
            else:
                print("❌ Failed to query document back.")
        else:
            print("❌ API Request failed.")
            
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == "__main__":
    test_upload_endpoint()
