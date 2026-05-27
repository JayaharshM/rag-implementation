from fastapi.testclient import TestClient
from app.main import app, vector_store
import fitz
import os

client = TestClient(app)

def create_sample_pdf(file_path):
    doc = fitz.open()
    page = doc.new_page()
    text = "The unique secret password to the vault is 'Orion-Seven-Delta'. Keep it safe."
    rect = fitz.Rect(50, 50, 550, 800)
    page.insert_textbox(rect, text, fontsize=12)
    doc.save(file_path)
    doc.close()

def test_query_endpoint():
    pdf_path = "query_test.pdf"
    test_user_id = "agent_007"
    
    try:
        print("1. Creating a sample PDF with specific knowledge...")
        create_sample_pdf(pdf_path)
        
        print("2. Uploading the PDF for user 'agent_007'...")
        with open(pdf_path, "rb") as f:
            upload_res = client.post(
                "/upload",
                files={"file": ("query_test.pdf", f, "application/pdf")},
                data={"user_id": test_user_id}
            )
        
        if upload_res.status_code != 200:
            print("❌ Upload failed:", upload_res.text)
            return
            
        print("✅ Upload successful!")
        
        print("\n3. Testing the /query endpoint...")
        query_res = client.post(
            "/query",
            json={
                "user_id": test_user_id,
                "message": "What is the secret password to the vault?"
            }
        )
        
        print(f"Status Code: {query_res.status_code}")
        
        if query_res.status_code == 200:
            data = query_res.json()
            context = data.get("context", [])
            print(f"Returned Context Chunks: {len(context)}")
            
            if len(context) > 0:
                print("\n✅ Query Endpoint Successful! Top chunk returned:")
                print(f"'{context[0]}'")
                
                if "Orion-Seven-Delta" in context[0]:
                    print("\n🎯 Confirmed: The relevant chunk was retrieved!")
                else:
                    print("\n❌ The retrieved chunk does not contain the expected answer.")
            else:
                print("❌ No context chunks returned.")
        else:
            print("❌ Query request failed:", query_res.text)
            
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == "__main__":
    test_query_endpoint()
