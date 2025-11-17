import requests
import os
from typing import Optional

DEFAULT_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
TIMEOUT_SECONDS = 90

class OllamaClient:
    def __init__(self, host: str, model: str):
        self.host = host.rstrip('/')
        self.model = model
        self.url = f"{self.host}/api/generate"

    def generate(self, prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> Optional[str]:
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            response = requests.post(self.url, json=payload, timeout=TIMEOUT_SECONDS)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
        except Exception as e:
            print(f"Ollama error: {e}")
            return None