````markdown
# KB Ingestor

**KB Ingestor** is a lightweight API service designed to support ingestion, chunking, embedding, and vector search of knowledge base content. It integrates with PostgreSQL + pgvector and uses Amazon Bedrock for embeddings (e.g., Titan model).

---

## 🚀 Features

- 🔹 Chunk raw text into overlapping sections
- 🔹 Generate embeddings using Amazon Bedrock
- 🔹 Store chunks in a vector-enabled PostgreSQL table
- 🔹 Search via vector similarity with optional metadata filters
- 🔹 Delete chunks by metadata (with dry-run support)

---

## 📦 Requirements

- Python 3.10+
- PostgreSQL with `pgvector` extension
- Amazon Bedrock access (Titan embedding model)
- `psycopg2`, `boto3`, `fastapi`, `uvicorn`, `python-dotenv`

---

## 🔧 Installation

```bash
git clone https://github.com/yourname/kb_ingestor.git
cd kb_ingestor
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
````

Add a `.env` file:

```dotenv
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=your_region
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db
DB_USER=your_user
DB_PASS=your_pass
```

---

## 🏁 Running the App

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8888
```

---

## 📚 API Endpoints

### `/embed` – Generate Embedding

```json
POST /embed
{
  "text": "your content"
}
```

---

### `/upsert` – Insert Chunked Text & Embeddings

```json
POST /upsert
{
  "doc_id": "mydoc1",
  "text": "Some long text to be chunked...",
  "chunk": true,
  "metadata": {
    "document_id": "mydoc1",
    "namespace": "example"
  },
  "table_name": "api_chunks"
}
```

---

### `/search` – Find Similar Documents

```json
POST /search
{
  "embedding": [...],
  "metadata": {
    "document_id": "mydoc1"
  },
  "top_k": 5,
  "table_name": "api_chunks"
}
```

Returns matching documents sorted by distance.

---

### `/delete` – Delete Chunks by Metadata

```json
POST /delete
{
  "metadata": {
    "document_id": "mydoc1"
  },
  "table_name": "api_chunks",
  "dry_run": true
}
```

Use `dry_run = true` to preview deletions without executing.

---

## 🧪 Testing

```bash
pytest tests/
```

Test cases simulate full flow: embedding → upsert → search.

---

## 📁 Folder Structure

```
kb_ingestor/
│
├── app/
│   ├── main.py               # FastAPI app
│   ├── vector_store.py       # DB interaction
│   ├── embedder.py           # Bedrock embed logic
│   ├── chunker.py            # Text splitting
│
├── tests/
│   └── test_search.py        # Basic test example
│
└── .env                      # Environment variables
```

---

## 🧠 Future Ideas

* Add support for multiple embedding providers
* UI for interactive ingestion and query
* CLI mode
* Async PG driver for performance

---

## 📃 License

MIT License – feel free to use, contribute, or fork this for your own needs.

---

```