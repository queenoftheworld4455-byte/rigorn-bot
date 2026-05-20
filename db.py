from sqlalchemy import create_engine, text
from config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL)


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
        logger.error(f"DB insert failed: {e}")