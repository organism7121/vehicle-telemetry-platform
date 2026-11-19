import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PW = os.getenv("POSTGRES_PW")
HOST = os.getenv("HOST")

def query(sql, params = None):
    with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PW, host=HOST, port=6543) as conn:
        with conn.cursor() as cur:
            if type(params) == list:
                cur.executemany(sql, params)
            else:
                cur.execute(sql, params)
            return cur.fetchall() if cur.description else None

# might be better to define the table outside the script/program
def create_table():
    query("""
        CREATE TABLE IF NOT EXISTS can_data (
            time TIMESTAMPTZ NOT NULL,
            frame_id INT NOT NULL,
            msg TEXT,
            signal TEXT,
            val DOUBLE PRECISION
        );
    """)

def insert_batch(rows):
    query("""
        INSERT INTO can_data
        (time, frame_id, msg, signal, val)
        VALUES (to_timestamp(%s), %s, %s, %s, %s);
    """, rows)



