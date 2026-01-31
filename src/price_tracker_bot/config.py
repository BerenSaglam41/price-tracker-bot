from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str
    webhook_url: str | None
    port: int

def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    db_url = os.getenv("DATABASE_URL", "").strip()
    webhook_url = os.getenv("WEBHOOK_URL", "").strip() or None
    port = int(os.getenv("PORT", "8080"))
    
    if not token:
        raise RuntimeError("BOT_TOKEN is missing. Create a .env file based on .env.example")
    if not db_url:
        raise RuntimeError("DATABASE_URL is missing. Create a .env file based on .env.example")
    
    # Render postgres:// URL'ini asyncpg uyumlu hale getir
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    return Settings(
        bot_token=token,
        database_url=db_url,
        webhook_url=webhook_url,
        port=port
    )