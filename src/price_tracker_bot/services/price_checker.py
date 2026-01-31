"""Otomatik fiyat kontrol servisi"""
from __future__ import annotations

import asyncio
from datetime import datetime

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..db.repo.tracking_repo import TrackingRepo
from .product_enrichment import product_service


class PriceCheckerService:
    """Periyodik olarak ürün fiyatlarını kontrol eder"""
    
    def __init__(self, bot: Bot, sessionmaker: async_sessionmaker[AsyncSession]):
        self.bot = bot
        self.sessionmaker = sessionmaker
    
    async def check_all_prices(self):
        """Tüm aktif ürünlerin fiyatlarını kontrol et"""
        async with self.sessionmaker() as session:
            try:
                repo = TrackingRepo(session)
                
                # Tüm aktif ürünleri al
                items = await repo.list_active()
                
                print(f"[{datetime.now()}] Checking {len(items)} active items...")
                
                for item in items:
                    try:
                        # Ürün bilgilerini çek
                        product_info = await product_service.fetch_product_info(item.url)
                        
                        if not product_info.price:
                            continue
                        
                        current_price = product_info.price
                        old_price = item.last_price or item.baseline_price
                        
                        # Fiyat düştü mü kontrol et
                        if current_price < old_price:
                            price_drop_pct = ((old_price - current_price) / old_price) * 100
                            
                            # Eşik kontrolü
                            if price_drop_pct >= item.threshold_pct:
                                # Kullanıcıya bildirim gönder
                                await self._send_price_drop_notification(
                                    item, 
                                    old_price, 
                                    current_price, 
                                    price_drop_pct
                                )
                        
                        # Fiyatı güncelle
                        await repo.update_price(item.id, current_price)
                        
                        # Rate limiting için kısa bekleme
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        print(f"Error checking item {item.id}: {e}")
                        await session.rollback()
                        continue
                
                # Tüm değişiklikleri commit et
                await session.commit()
                
            except Exception as e:
                print(f"Error in price checker: {e}")
                await session.rollback()
    
    async def _send_price_drop_notification(
        self, 
        item, 
        old_price: float, 
        new_price: float, 
        drop_pct: float
    ):
        """Fiyat düşüş bildirimi gönder"""
        try:
            message = (
                f"🎉 **Fiyat Düştü!**\n\n"
                f"📦 {item.title or 'Ürün'}\n\n"
                f"💰 Eski fiyat: {old_price:.2f} TL\n"
                f"💰 Yeni fiyat: **{new_price:.2f} TL**\n"
                f"📉 Düşüş: %{drop_pct:.1f}\n\n"
                f"🔗 [Ürüne Git]({item.url})"
            )
            
            await self.bot.send_message(
                chat_id=item.chat_id,
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            print(f"✅ Notification sent for item {item.id}")
        except Exception as e:
            print(f"Failed to send notification for item {item.id}: {e}")
