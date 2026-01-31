import asyncio
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import load_settings
from .db.engine import build_engine, build_sessionmaker
from .bot.dispatcher import build_dispatcher
from .services.price_checker import PriceCheckerService

async def main() -> None:
    settings = load_settings()
    bot = Bot(token=settings.bot_token)

    engine = build_engine(settings.database_url)
    sessionmaker = build_sessionmaker(engine)

    dp = build_dispatcher(sessionmaker)
    
    # Otomatik fiyat kontrolü için scheduler
    price_checker = PriceCheckerService(bot, sessionmaker)
    scheduler = AsyncIOScheduler()
    
    # Her 5 dakikada bir fiyat kontrolü yap
    scheduler.add_job(
        price_checker.check_all_prices,
        'interval',
        minutes=5,
        id='price_checker',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Scheduler başlatıldı - Her 5 dakikada fiyat kontrolü yapılacak")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())