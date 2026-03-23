import sqlite3
import os
from contextlib import contextmanager
from app.core.config import BASE_DIR

# Ensure data directory exists
data_dir = os.path.join(BASE_DIR, "data")
os.makedirs(data_dir, exist_ok=True)
DB_PATH = os.path.join(data_dir, "documents.db")

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