from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        async with self._sessionmaker() as session:
            data["db_session"] = session
            try:
                result = await handler(event, data)
                # Handler başarılı olduysa commit yap
                if not session.is_active:
                    # Session zaten rollback yapılmış, commit etme
                    return result
                await session.commit()
                return result
            except Exception as e:
                # Hata olursa rollback yap
                if session.is_active:
                    await session.rollback()
                # Exception'ı handler'a fırlat (handler kendi mesajını gösterecek)
                raise