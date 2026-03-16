import sqlite3

DB_PATH = "data/documents.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn


def create_tables():

    conn = get_connection()
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
    conn.close()