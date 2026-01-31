"""Database initialization script"""
import asyncio
from src.price_tracker_bot.config import load_settings
from src.price_tracker_bot.db.engine import build_engine
from src.price_tracker_bot.db.base import Base
from src.price_tracker_bot.db.models import TrackingItem

async def init_db():
    """Create all tables"""
    settings = load_settings()
    engine = build_engine(settings.database_url)
    
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ Old tables dropped")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("✅ New tables created")
    
    await engine.dispose()
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
