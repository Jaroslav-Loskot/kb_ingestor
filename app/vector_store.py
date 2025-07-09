# app/vector_store.py
from typing import Any, Dict, Optional
import psycopg2
import json
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgres")


def upsert_document(text: str, embedding: list[float], metadata: dict, table_name: str = "documents"):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {table_name} (content, embedding, metadata)
            VALUES (%s, %s, %s)
        """, (
            text,
            embedding,
            json.dumps(metadata)
        ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error inserting document: {e}")
        raise


def delete_by_document_id(document_id: str, table_name: str = "documents"):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        cur.execute(f"""
            DELETE FROM {table_name}
            WHERE metadata->>'document_id' = %s
        """, (document_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error deleting documents: {e}")
        raise


def search_similar(query_embedding, top_k=5, metadata_filter=None, table_name="documents"):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()

        # Convert embedding to pgvector-compatible string
        embedding_str = f"[{', '.join(map(str, query_embedding))}]"

        # Base query
        query = f"""
            SELECT id, content, metadata, embedding <-> (%s::vector) AS distance
            FROM {table_name}
        """

        # Where clause (optional metadata filter)
        params = [embedding_str]
        if metadata_filter:
            for key, value in metadata_filter.items():
                query += f" WHERE metadata ->> %s = %s"
                params.extend([key, str(value)])
                break  # only apply one filter for now, adjust if you want AND/OR support

        # Add ordering and limit
        query += " ORDER BY distance ASC LIMIT %s"
        params.append(top_k)

        cur.execute(query, params)
        rows = cur.fetchall()

        results = [
            {
                "id": row[0],
                "content": row[1],
                "metadata": row[2],
                "distance": row[3],
            }
            for row in rows
        ]

        cur.close()
        conn.close()
        return results

    except Exception as e:
        print(f"❌ Error in search_similar: {e}")
        raise


def delete_by_metadata_filter(metadata_filter: dict | None, table_name: str = "documents", dry_run: bool = False):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()

        conditions = []
        values = []

        if metadata_filter:
            for key, value in metadata_filter.items():
                conditions.append(f"metadata ->> %s = %s")
                values.extend([key, str(value)])

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        if dry_run:
            cur.execute(
                f"SELECT id, content, metadata FROM {table_name} WHERE {where_clause}",
                tuple(values)
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows  # return matched rows only

        cur.execute(
            f"DELETE FROM {table_name} WHERE {where_clause}",
            tuple(values)
        )
        deleted = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()

        return deleted
    except Exception as e:
        print(f"❌ Error during deletion: {e}")
        raise
