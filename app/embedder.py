# app/embedder.py
import json
import logging
import os

import boto3
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")


bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

def embed_text(text: str) -> list[float]:
    if not text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty.")

    try:
        payload = {"inputText": text}
        response = bedrock_client.invoke_model(
            modelId=EMBEDDING_MODEL_ID,
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json",
        )
        body = response["body"].read().decode()
        result = json.loads(body)

        embedding = result.get("embedding")
        if not embedding or not isinstance(embedding, list):
            raise HTTPException(status_code=500, detail="Invalid embedding structure.")

        return embedding

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")
