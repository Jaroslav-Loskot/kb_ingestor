# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.embedder import embed_text
from app.vector_store import upsert_document, search_similar
from app.chunker import chunk_text

app = FastAPI()

# Request models
class EmbedRequest(BaseModel):
    text: str

class DeleteRequest(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
    table_name: Optional[str] = "documents"
    dry_run: Optional[bool] = False



class UpsertRequest(BaseModel):
    doc_id: str
    text: str
    chunk: Optional[bool] = True  # Default to chunking
    chunk_size: Optional[int] = 500
    overlap: Optional[int] = 100
    metadata: Dict[str, Any]  # Now mandatory
    table_name: Optional[str] = "documents"

class SearchRequest(BaseModel):
    embedding: List[float]
    metadata: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = 5
    table_name: Optional[str] = "documents"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/embed")
async def embed_api(request: EmbedRequest):
    embedding = embed_text(request.text)
    return {"embedding": embedding, "dim": len(embedding)}  # show sample only

@app.post("/upsert")
async def upsert(request: UpsertRequest):
    try:
        from app.vector_store import delete_by_document_id

        document_id = request.metadata.get("document_id")
        if not document_id:
            raise HTTPException(status_code=400, detail="metadata.document_id is required")

        delete_by_document_id(document_id=document_id, table_name=request.table_name)

        if request.chunk:
            chunks = chunk_text(
                request.text,
                chunk_size=request.chunk_size or 500,
                overlap=request.overlap or 100
            )
            for chunk in chunks:
                embedding = embed_text(chunk)
                upsert_document(text=chunk, embedding=embedding, metadata=request.metadata, table_name=request.table_name)
            return {"status": "ok", "chunks": len(chunks)}
        else:
            embedding = embed_text(request.text)
            upsert_document(text=request.text, embedding=embedding, metadata=request.metadata, table_name=request.table_name)
            return {"status": "ok", "chunks": 1}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search(request: SearchRequest):
    try:
        results = search_similar(
            query_embedding=request.embedding,
            top_k=request.top_k,
            metadata_filter=request.metadata,
            table_name=request.table_name
        )
        return {
            "matches": results,
            "conditions": {
                "table_name": request.table_name,
                "metadata": request.metadata,
                "top_k": request.top_k
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/delete")
async def delete(request: DeleteRequest):
    try:
        from app.vector_store import delete_by_metadata_filter

        if request.dry_run:
            matches = delete_by_metadata_filter(
                metadata_filter=request.metadata,
                table_name=request.table_name,
                dry_run=True
            )
            return {
                "dry_run": True,
                "matched": len(matches),
                "rows": [
                    {
                        "id": row[0],
                        "content": row[1],
                        "metadata": row[2]
                    } for row in matches
                ],
                "conditions": {
                    "table_name": request.table_name,
                    "metadata": request.metadata
                }
            }

        deleted_count = delete_by_metadata_filter(
            metadata_filter=request.metadata,
            table_name=request.table_name
        )

        return {
            "status": "ok",
            "deleted": deleted_count,
            "conditions": {
                "table_name": request.table_name,
                "metadata": request.metadata
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

