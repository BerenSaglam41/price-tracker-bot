from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str

def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    db_url = os.getenv("DATABASE_URL", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is missing. Create a .env file based on .env.example")
    if not db_url:
        raise RuntimeError("DATABASE_URL is missing. Create a .env file based on .env.example")
    return Settings(bot_token=token, database_url=db_url)