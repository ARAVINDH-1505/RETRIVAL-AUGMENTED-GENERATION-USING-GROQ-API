import sqlite3
import os
from contextlib import contextmanager

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
DB_PATH = "data/documents.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def create_tables():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT,
            file_hash TEXT,
            upload_time TEXT
        )
        """)
        conn.commit()