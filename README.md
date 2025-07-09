# KB Ingestor

**KB Ingestor** is a FastAPI-based service for embedding and storing knowledge base content in a PostgreSQL database with `pgvector`. It supports document chunking, semantic vector search, metadata filtering, and content deletion.

---

## 🚀 Features

- Embed text with Amazon Titan (via Bedrock)
- Store documents in PostgreSQL using `pgvector`
- Automatic chunking of large documents
- Metadata support (e.g., `document_id`, `namespace`, etc.)
- Similarity search using embeddings
- Metadata-based deletion
- Dry-run mode for safe deletions
- Health check endpoint (`/health`)

---

## 🧾 Requirements

- Python 3.10+
- Docker + Docker Compose
- AWS account with access to Amazon Bedrock

---

## 📦 Environment Setup

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
PG_HOST=postgres
PG_PORT=5432
PG_DB=kb_db
PG_USER=kb_user
PG_PASSWORD=kb_pass
```

---

## 🐳 Docker Compose

Run the stack:

```bash
docker-compose up --build
```

PostgreSQL with `pgvector` and the FastAPI service will be ready at:

- API: http://localhost:8888
- Health Check: http://localhost:8888/health

---

## 🔍 API Endpoints

### `POST /embed`
Get an embedding for a given text.

```json
{
  "text": "Your sentence here"
}
```

---

### `POST /upsert`
Chunk (if needed), embed, and store document(s).

```json
{
  "doc_id": "your-id",
  "text": "Long or short document content...",
  "chunk": true,
  "chunk_size": 300,
  "overlap": 50,
  "metadata": {
    "document_id": "doc-123",
    "namespace": "api-docs"
  },
  "table_name": "api_chunks"
}
```

If content with the same `document_id` exists, it will be deleted before insert.

---

### `POST /search`
Find similar documents.

```json
{
  "embedding": [0.123, 0.456, ...],
  "metadata": {
    "document_id": "doc-123"
  },
  "top_k": 5,
  "table_name": "api_chunks"
}
```

---

### `POST /delete`
Delete documents by metadata filter.

```json
{
  "metadata": {
    "document_id": "doc-123"
  },
  "table_name": "api_chunks",
  "dry_run": false
}
```

If `dry_run: true`, it shows how many documents *would* be deleted.

---

### `GET /health`
Simple service status check.

---

## 🧪 Tests

```bash
pytest -s tests/test_search.py
```

Make sure the server is running before executing tests.

---

## 📁 Folder Structure

```text
kb-ingestor/
├── app/
│   ├── main.py           # FastAPI entrypoint
│   ├── embedder.py       # Embedding via Bedrock
│   ├── chunker.py        # Chunking logic
│   └── vector_store.py   # PostgreSQL upsert/search/delete
├── tests/
│   └── test_search.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## 🧠 Notes
- Only Titan embeddings (1024-d) are supported for now.
- Adjust chunk size and overlap for best semantic segmentation.

---

## ❤️ Contributions
PRs welcome!

---

## 📜 License
MIT
