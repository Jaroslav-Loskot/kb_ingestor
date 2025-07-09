# app/chunker.py
import re

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            # Add overlap if needed
            current_chunk = sentence[-overlap:] + " " if overlap > 0 else sentence + " "
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks
