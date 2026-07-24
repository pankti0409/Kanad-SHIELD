import asyncio
import os
from pathlib import Path

async def reset_database():
    from app.database.engine import engine
    from app.database.base import Base
    from app.models import User, Case, Recording, Entity, ThreatIndicator, AuditLog, EvidenceFile

    # Dispose connection pool first
    await engine.dispose()

    db_file = Path("test.db")
    if db_file.exists():
        try:
            db_file.unlink()
            print("Existing database file test.db removed.")
        except Exception as e:
            print(f"Could not remove file: {e}")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print("Database cleared and fresh schema initialized successfully.")

if __name__ == "__main__":
    asyncio.run(reset_database())
