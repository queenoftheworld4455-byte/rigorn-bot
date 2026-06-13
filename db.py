from sqlalchemy import create_engine, text
from config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)

def create_table():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS applications (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT NOW(),
                lang TEXT,
                interest TEXT,
                city TEXT,
                budget TEXT,
                payment TEXT,
                phone TEXT,
                extra TEXT
            )
        """))

def create_files_table():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            code TEXT UNIQUE,
            file_id TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
        """))
        
def save_file(code, file_id):
    with engine.begin() as conn:
        conn.execute(
            text("""
            INSERT INTO files (code, file_id)
            VALUES (:code, :file_id)
            ON CONFLICT (code)
            DO UPDATE SET file_id = :file_id
            """),
            {
                "code": code,
                "file_id": file_id
            }
        )

def get_file(code):
    with engine.begin() as conn:
        result = conn.execute(
            text("""
            SELECT file_id
            FROM files
            WHERE code=:code
            """),
            {"code": code}
        ).fetchone()

    return result[0] if result else None

def save_to_db(data):
    query = text("""
        INSERT INTO applications
        (lang, interest, city, budget, payment, phone, extra)
        VALUES
        (:lang, :interest, :city, :budget, :payment, :phone, :extra)
    """)

    try:
        with engine.begin() as conn:
            conn.execute(query, {
                "lang": data.get("lang"),
                "interest": data.get("interest"),
                "city": data.get("city"),
                "budget": data.get("budget"),
                "payment": data.get("payment"),
                "phone": data.get("phone"),
                "extra": data.get("extra"),
            })

    except Exception as e:
        print(e)
        logger.error(f"DB insert failed: {e}")
        


        