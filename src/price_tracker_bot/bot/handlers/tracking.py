from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.repo.tracking_repo import TrackingRepo
from ...services.product_enrichment import product_service
from ..keyboards import after_add_kb, tracking_item_kb

router = Router()

def _parse_url_arg(text: str) -> str | None:
    parts = text.strip().split(maxsplit=1)
    if len(parts) < 2:
        return None
    return parts[1].strip()

@router.message(Command("add"))
async def add_tracking(message: Message, db_session: AsyncSession) -> None:
    url = _parse_url_arg(message.text or "")
    if not url:
        await message.answer("Kullanım: /add <url>\nÖrnek: /add https://trendyol.com/urun")
        return

    # Bilgilendirme mesajı
    status_msg = await message.answer("🔍 Ürün bilgileri çekiliyor...")
    
    repo = TrackingRepo(db_session)
    
    try:
        # URL'den ürün bilgilerini çek
        product_info = await product_service.fetch_product_info(url)
        
        # Fiyat yoksa ekleme
        if not product_info.price:
            await status_msg.delete()
            await message.answer(
                "❌ Fiyat bilgisi çekilemedi!\n\n"
                "Ürün takibe alınamadı. Lütfen:\n"
                "• URL'yi kontrol edin\n"
                "• Farklı bir ürün linkini deneyin\n"
                "• Daha sonra tekrar deneyin"
            )
            return
        
        # Database'e kaydet
        item = await repo.add(
            chat_id=message.chat.id,
            url=url,
            baseline_price=product_info.price,
            title=product_info.title,
            image_url=product_info.image_url
        )

        # Mesajı güncelle
        await status_msg.delete()

        # Sonuç mesajı
        result_text = "✅ Takibe alındı!\n\n"
        
        if product_info.title:
            result_text += f"📦 **{product_info.title}**\n\n"
        
        result_text += f"💰 Referans fiyat: **{product_info.price:.2f} {product_info.currency}**\n"
        
        result_text += f"🆔 ID: {item.id}\n"
        result_text += f"🔗 [Link]({url})\n\n"
        result_text += "Fiyat düşünce bildirim göndereceğim! 🔔"

        has_image = bool(product_info.image_url)
        
        await message.answer(
            result_text,
            reply_markup=after_add_kb(item_id=item.id, has_image=has_image),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

    except Exception as e:
        # Session'da hata varsa rollback yap
        await db_session.rollback()
        await status_msg.delete()
        await message.answer(
            f"❌ Takip eklenemedi.\n\n"
            f"Hata: {str(e)[:200]}"
        )

@router.message(Command("list"))
async def list_tracking(message: Message, db_session: AsyncSession) -> None:
    repo = TrackingRepo(db_session)
    items = await repo.list_by_chat(chat_id=message.chat.id)

    if not items:
        await message.answer("Henüz takip yok. /add ile link ekleyebilirsin.")
        return

    await message.answer(f"📋 Toplam {len(items)} takip bulundu:")

    for it in items:
        status = "🟢 aktif" if it.is_active else "🟡 durduruldu"
        
        # Başlık varsa göster
        title_text = f"📦 **{it.title}**\n\n" if it.title else ""
        
        text = (
            f"{title_text}"
            f"🆔 ID: {it.id} — {status}\n"
            f"💰 Referans: {it.baseline_price:.2f} TL\n"
            f"💵 Son fiyat: {it.last_price:.2f} TL\n"
            f"🎯 Eşik: %{it.threshold_pct}\n"
            f"🔗 [Link]({it.url})"
        )
        
        has_image = bool(it.image_url or it.telegram_file_id)
        
        await message.answer(
            text,
            reply_markup=tracking_item_kb(item_id=it.id, is_active=it.is_active, has_image=has_image),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )