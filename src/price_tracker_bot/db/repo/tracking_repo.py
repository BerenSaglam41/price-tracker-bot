from __future__ import annotations

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import TrackingItem

class TrackingRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(
        self,
        chat_id: int,
        url: str,
        baseline_price: float,
        title: str | None = None,
        image_url: str | None = None,
    ) -> TrackingItem:
        item = TrackingItem(
            chat_id=chat_id,
            url=url,
            baseline_price=baseline_price,
            last_price=baseline_price,
            title=title,
            image_url=image_url,
        )
        self.session.add(item)
        # flush() yaparak ID'yi hemen al, middleware commit yapacak
        # Eğer flush() hata verirse exception fırlatır, middleware rollback yapar
        await self.session.flush()
        return item

    async def list_by_chat(self, chat_id: int) -> list[TrackingItem]:
        q = select(TrackingItem).where(TrackingItem.chat_id == chat_id).order_by(TrackingItem.id.desc())
        res = await self.session.execute(q)
        return list(res.scalars().all())

    async def get(self, chat_id: int, item_id: int) -> TrackingItem | None:
        q = select(TrackingItem).where(TrackingItem.chat_id == chat_id, TrackingItem.id == item_id)
        res = await self.session.execute(q)
        return res.scalar_one_or_none()

    async def remove(self, chat_id: int, item_id: int) -> bool:
        q = delete(TrackingItem).where(TrackingItem.chat_id == chat_id, TrackingItem.id == item_id)
        res = await self.session.execute(q)
        return (res.rowcount or 0) > 0

    async def set_active(self, chat_id: int, item_id: int, active: bool) -> bool:
        q = (
            update(TrackingItem)
            .where(TrackingItem.chat_id == chat_id, TrackingItem.id == item_id)
            .values(is_active=active)
        )
        res = await self.session.execute(q)
        return (res.rowcount or 0) > 0

    async def set_threshold(self, chat_id: int, item_id: int, pct: float) -> bool:
        if pct < 0:
            pct = 0.0
        q = (
            update(TrackingItem)
            .where(TrackingItem.chat_id == chat_id, TrackingItem.id == item_id)
            .values(threshold_pct=float(pct))
        )
        res = await self.session.execute(q)
        return (res.rowcount or 0) > 0

    async def set_telegram_file_id(self, chat_id: int, item_id: int, file_id: str) -> bool:
        q = (
            update(TrackingItem)
            .where(TrackingItem.chat_id == chat_id, TrackingItem.id == item_id)
            .values(telegram_file_id=file_id)
        )
        res = await self.session.execute(q)
        return (res.rowcount or 0) > 0
    
    async def list_active(self) -> list[TrackingItem]:
        """Tüm aktif ürünleri getir"""
        q = select(TrackingItem).where(TrackingItem.is_active == True)
        res = await self.session.execute(q)
        return list(res.scalars().all())
    
    async def update_price(self, item_id: int, new_price: float) -> bool:
        """Ürünün son fiyatını güncelle"""
        q = (
            update(TrackingItem)
            .where(TrackingItem.id == item_id)
            .values(last_price=new_price)
        )
        res = await self.session.execute(q)
        return (res.rowcount or 0) > 0