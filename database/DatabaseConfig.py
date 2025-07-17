import os
from dotenv import load_dotenv

load_dotenv()

DB_BACKEND = os.getenv("DB_BACKEND", "sqlite").lower()

MYSQL_CONFIG = {
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "test")
}

SQLITE_PATH = os.getenv("SQLITE_PATH", "database.db")
