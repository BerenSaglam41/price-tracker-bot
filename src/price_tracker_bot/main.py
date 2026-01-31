import asyncio
from aiogram import Bot
from aiogram.types import Update
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web

from .config import load_settings
from .db.engine import build_engine, build_sessionmaker
from .db.base import Base
from .bot.dispatcher import build_dispatcher
from .services.price_checker import PriceCheckerService

async def init_database(engine):
    """Veritabanı tablolarını oluştur"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")

async def health_check(request):
    """Health check endpoint for Render"""
    return web.Response(text="OK", status=200)

async def main() -> None:
    settings = load_settings()
    
    # Debug: Hangi database kullanıldığını göster
    print(f"📊 Database URL: {settings.database_url[:50]}...")
    
    bot = Bot(token=settings.bot_token)

    engine = build_engine(settings.database_url)
    sessionmaker = build_sessionmaker(engine)
    
    # Veritabanı tablolarını oluştur (yoksa)
    await init_database(engine)

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
    
    # Webhook veya polling modunu seç
    if settings.webhook_url:
        # Webhook modu (Render için)
        print(f"🌐 Webhook modu - {settings.webhook_url}")
        
        # Webhook'u ayarla
        webhook_path = "/webhook"
        await bot.set_webhook(
            url=f"{settings.webhook_url}{webhook_path}",
            drop_pending_updates=True
        )
        
        # Webhook handler - Update objesini düzgün parse et
        async def webhook_handler(request):
            try:
                update_dict = await request.json()
                # Dict'i Update objesine çevir
                update = Update(**update_dict)
                # Bot instance'ını ekle
                update.bot = bot
                # Dispatcher'a gönder
                await dp.feed_update(bot, update)
                return web.Response(text="OK", status=200)
            except Exception as e:
                print(f"❌ Webhook error: {e}")
                return web.Response(text="ERROR", status=500)
        
        # Aiohttp app oluştur
        app = web.Application()
        app.router.add_post(webhook_path, webhook_handler)
        app.router.add_get("/health", health_check)
        
        # Web sunucuyu başlat
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', settings.port)
        await site.start()
        
        print(f"✅ Bot webhook modunda çalışıyor - Port: {settings.port}")
        print(f"✅ Health check: http://0.0.0.0:{settings.port}/health")
        print(f"✅ Webhook: {settings.webhook_url}{webhook_path}")
        
        # Sonsuza kadar çalışmaya devam et
        await asyncio.Event().wait()
    else:
        # Polling modu (Local için)
        print("🔄 Polling modu - Local development")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())