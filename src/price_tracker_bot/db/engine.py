from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

def build_engine(database_url: str):
    return create_async_engine(database_url, pool_pre_ping=True)

def build_sessionmaker(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)