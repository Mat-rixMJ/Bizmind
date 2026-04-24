import requests
import json
import os
from dotenv import load_dotenv

load_dotenv("d:/agent1/bizmind/.env")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5")

payload = {
    "model": OLLAMA_MODEL,
    "messages": [
        {"role": "user", "content": "Hello! Reply 'BizMind connected!' if you are receiving this."}
    ],
    "stream": False
}

try:
    print(f"Connecting to Local Ollama using model: {OLLAMA_MODEL}...")
    response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=20)
    if response.status_code == 200:
        content = response.json().get("message", {}).get("content", "")
        print(f"SUCCESS. Response from {OLLAMA_MODEL}: {content}")
    else:
        print(f"FAILED. Status Code: {response.status_code}, Response: {response.text}")
except Exception as e:
    print(f"ERROR: {str(e)}")
