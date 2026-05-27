import requests
import os
import json

class LLMClient:
    def __init__(self):
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://192.168.1.40:11434")
        self.model = os.environ.get("OLLAMA_LLM_MODEL", "qwen2.5:3b")

    def generate_stream(self, prompt: str):
        """
        Calls Ollama generate endpoint with stream=True and yields the response chunks.
        """
        url = f"{self.base_url}/api/generate"
        response = requests.post(url, json={
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }, stream=True)
        
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                if "response" in data:
                    yield data["response"]
