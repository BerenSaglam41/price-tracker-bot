from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

def build_engine(database_url: str):
    """
    Create database engine with optimized settings for cloud deployment
    """
    # PostgreSQL için connection pool ayarları
    if "postgresql" in database_url:
        return create_async_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=5,  # Render free tier için optimize edilmiş
            max_overflow=10,
            pool_recycle=3600,  # 1 saatte bir connection'ları yenile
            echo=False
        )
    # SQLite için basit ayarlar
    else:
        return create_async_engine(
            database_url,
            pool_pre_ping=True,
            echo=False
        )

def build_sessionmaker(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)