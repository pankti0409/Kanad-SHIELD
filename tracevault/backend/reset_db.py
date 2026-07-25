import asyncio
import os
import sys
from pathlib import Path

# Add backend dir to python path
sys.path.append(str(Path(__file__).parent.absolute()))

async def reset_database():
    from app.config import get_settings
    from app.database.engine import engine, create_all_tables
    from app.database.base import Base
    # Force import of all models for registration
    import app.models  # noqa: F401

    settings = get_settings()
    db_url = settings.db.DATABASE_URL
    is_sqlite = "sqlite" in db_url.lower()

    # Close existing engine pool
    await engine.dispose()

    if is_sqlite:
        # Extract filename from sqlite+aiosqlite:///./tracevault_dev.db
        db_path = db_url.split("///")[-1]
        db_file = Path(db_path)
        if db_file.exists():
            try:
                # Remove database file and wal/shm files
                db_file.unlink()
                for suffix in [".db-wal", ".db-shm", "-wal", "-shm"]:
                    wal_file = Path(str(db_file) + suffix)
                    if wal_file.exists():
                        wal_file.unlink()
                print(f"Existing SQLite database files removed: {db_file}")
            except Exception as e:
                print(f"Could not remove database files: {e}")

    # Re-create all tables
    await create_all_tables()
    print("Database cleared and fresh schema initialized successfully.")

if __name__ == "__main__":
    asyncio.run(reset_database())
