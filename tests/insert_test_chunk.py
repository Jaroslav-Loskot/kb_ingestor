# insert_test_chunk.py
import os
import psycopg2
from dotenv import load_dotenv
from app.embedder import embed_text

load_dotenv()

# Connect to DB using .env variables
DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = os.getenv("PG_PORT", "5432")
DB_NAME = os.getenv("PG_DB", "postgres")
DB_USER = os.getenv("PG_USER", "postgres")
DB_PASS = os.getenv("PG_PASSWORD", "password")

TEXT = "Authenticate user with POST /auth/login"
DOC_ID = "test-login"

embedding = embed_text(TEXT)

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
    )
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO api_chunks (id, content, embedding)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET content = EXCLUDED.content,
            embedding = EXCLUDED.embedding;
    """, (DOC_ID, TEXT, embedding))

    conn.commit()
    print(f"✅ Inserted: {DOC_ID}")

    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Insert failed: {e}")
