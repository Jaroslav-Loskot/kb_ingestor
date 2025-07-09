# scripts/upload_txt.py

import os
import json
import requests

API_URL = "http://localhost:8888/upsert"
TXT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
TABLE_NAME = "api_chunks"

def main():
    if not os.path.exists(TXT_DIR):
        print(f"[ERROR] Directory not found: {TXT_DIR}")
        return

    txt_files = [f for f in os.listdir(TXT_DIR) if f.endswith(".txt")]
    if not txt_files:
        print(f"[INFO] No .txt files found in {TXT_DIR}")
        return

    for filename in txt_files:
        file_path = os.path.join(TXT_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        if not text:
            print(f"[WARN] Skipping empty file: {filename}")
            continue

        payload = {
            "text": text,
            "chunk": False,
            "metadata": {
                "document_id": os.path.splitext(filename)[0],
                "namespace": "api-integration",
                "method" : "login-step/create"
            },
            "table_name": TABLE_NAME
        }

        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                print(f"[OK] Uploaded: {filename}")
            else:
                print(f"[ERROR] Failed to upload {filename}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[EXCEPTION] Upload failed for {filename}: {e}")

if __name__ == "__main__":
    main()
