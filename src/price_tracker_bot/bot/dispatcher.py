from aiogram import Dispatcher

from .handlers.start import router as start_router
from .handlers.tracking import router as tracking_router
from .handlers.callbacks import router as callbacks_router
from .middlewares.db import DbSessionMiddleware

def build_dispatcher(sessionmaker) -> Dispatcher:
    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(sessionmaker))

    dp.include_router(start_router)
    dp.include_router(tracking_router)
    dp.include_router(callbacks_router)
    return dp