import os

API_KEY: str = os.getenv("API_KEY", "secret-key-change-me")
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./db.sqlite3")
MAX_ACTIVITY_DEPTH: int = 3
