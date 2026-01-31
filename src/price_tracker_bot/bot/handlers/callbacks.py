from __future__ import annotations

import httpx
from aiogram import Router, Bot
from aiogram.types import CallbackQuery, BufferedInputFile, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from ..callbacks import TrackActionCb
from ..keyboards import tracking_item_kb, threshold_menu_kb
from ...db.repo.tracking_repo import TrackingRepo
from ...services.product_enrichment import product_service

router = Router()

def _item_text(it) -> str:
    status = "🟢 aktif" if it.is_active else "🟡 durduruldu"
    title_text = f"📦 **{it.title}**\n\n" if it.title else ""
    return (
        f"{title_text}"
        f"🆔 ID: {it.id} — {status}\n"
        f"💰 Referans: {it.baseline_price:.2f} TL\n"
        f"💵 Son: {it.last_price:.2f} TL\n"
        f"🎯 Eşik: %{it.threshold_pct}\n"
        f"🔗 [Link]({it.url})"
    )

@router.callback_query(TrackActionCb.filter())
async def on_track_action(query: CallbackQuery, callback_data: TrackActionCb, db_session: AsyncSession) -> None:
    chat_id = query.message.chat.id if query.message else query.from_user.id
    item_id = callback_data.item_id
    repo = TrackingRepo(db_session)

    if callback_data.action == "pause":
        ok = await repo.set_active(chat_id=chat_id, item_id=item_id, active=False)
        if not ok:
            await query.answer("Bulunamadı.", show_alert=True)
            return
        item = await repo.get(chat_id=chat_id, item_id=item_id)
        await query.answer("Durduruldu.")
        if query.message and item:
            has_image = bool(item.image_url or item.telegram_file_id)
            await query.message.edit_reply_markup(reply_markup=tracking_item_kb(item_id=item_id, is_active=item.is_active, has_image=has_image))
        return

    if callback_data.action == "resume":
        ok = await repo.set_active(chat_id=chat_id, item_id=item_id, active=True)
        if not ok:
            await query.answer("Bulunamadı.", show_alert=True)
            return
        item = await repo.get(chat_id=chat_id, item_id=item_id)
        await query.answer("Devam ettirildi.")
        if query.message and item:
            has_image = bool(item.image_url or item.telegram_file_id)
            await query.message.edit_reply_markup(reply_markup=tracking_item_kb(item_id=item_id, is_active=item.is_active, has_image=has_image))
        return

    if callback_data.action == "remove":
        ok = await repo.remove(chat_id=chat_id, item_id=item_id)
        if ok:
            await query.answer("Silindi.")
            if query.message:
                await query.message.edit_text("🗑 Bu takip silindi.")
        else:
            await query.answer("Bulunamadı.", show_alert=True)
        return

    if callback_data.action == "threshold_menu":
        item = await repo.get(chat_id=chat_id, item_id=item_id)
        if not item:
            await query.answer("Bulunamadı.", show_alert=True)
            return

        text = (
            "🎯 Bildirim eşiği\n\n"
            f"Mevcut eşik: %{item.threshold_pct}\n"
            "Seçim yap: fiyat, referans fiyatına göre en az seçtiğin yüzde kadar düşerse bildiririm.\n"
            "0% seçersen her düşüşte bildiririm."
        )

        await query.answer()
        if query.message:
            await query.message.answer(text, reply_markup=threshold_menu_kb(item_id=item_id))
        return

    if callback_data.action == "threshold_set":
        try:
            pct = float(callback_data.value or "0")
        except ValueError:
            pct = 0.0

        ok = await repo.set_threshold(chat_id=chat_id, item_id=item_id, pct=pct)
        if not ok:
            await query.answer("Kaydedilemedi.", show_alert=True)
            return

        item = await repo.get(chat_id=chat_id, item_id=item_id)
        await query.answer("Eşik kaydedildi ✅")
        if query.message and item:
            text = (
                "🎯 Bildirim eşiği\n\n"
                f"Mevcut eşik: %{item.threshold_pct}\n"
                "Seçim yap: fiyat, referans fiyatına göre en az seçtiğin yüzde kadar düşerse bildiririm.\n"
                "0% seçersen her düşüşte bildiririm."
            )
            await query.message.edit_text(text, reply_markup=threshold_menu_kb(item_id=item_id))
        return

    if callback_data.action == "back":
        item = await repo.get(chat_id=chat_id, item_id=item_id)
        if not item:
            await query.answer("Bulunamadı.", show_alert=True)
            return
        await query.answer()
        if query.message:
            has_image = bool(item.image_url or item.telegram_file_id)
            # Eğer mesaj fotolu mesajsa, edit yapamayız - yeni mesaj gönder
            if query.message.photo:
                try:
                    await query.message.delete()
                except:
                    pass
                await query.message.answer(
                    _item_text(item),
                    reply_markup=tracking_item_kb(item_id=item.id, is_active=item.is_active, has_image=has_image),
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            else:
                await query.message.edit_text(
                    _item_text(item),
                    reply_markup=tracking_item_kb(item_id=item.id, is_active=item.is_active, has_image=has_image),
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
        return

    if callback_data.action == "close":
        await query.answer()
        if query.message:
            await query.message.edit_text("✅ Menü kapatıldı.")
        return

    # Görseli göster
    if callback_data.action == "show_image":
        item = await repo.get(chat_id=chat_id, item_id=item_id)
        if not item:
            await query.answer("Bulunamadı.", show_alert=True)
            return
        
        # Telegram file_id varsa onu kullan (hızlı)
        if item.telegram_file_id:
            await query.answer()
            
            # Yenileme butonu ekle
            kb = InlineKeyboardBuilder()
            kb.button(text="🔄 Görseli Yenile", callback_data=TrackActionCb(action="refresh_image", item_id=item_id).pack())
            kb.button(text="⬅️ Geri", callback_data=TrackActionCb(action="back", item_id=item_id).pack())
            kb.adjust(1)
            
            caption = f"📦 {item.title or 'Ürün'}\n💰 {item.last_price:.2f} TL"
            
            try:
                await query.message.answer_photo(
                    photo=item.telegram_file_id,
                    caption=caption,
                    reply_markup=kb.as_markup()
                )
            except Exception as e:
                # File_id geçersizse URL'den çek
                await query.answer("Görsel yükleniyor...", show_alert=False)
                await _send_image_from_url(query, item, repo)
            return
        
        # URL'den çek
        if item.image_url:
            await query.answer("Görsel yükleniyor...", show_alert=False)
            await _send_image_from_url(query, item, repo)
        else:
            await query.answer("Bu ürünün görseli yok.", show_alert=True)
        return
    
    # Görseli yenile
    if callback_data.action == "refresh_image":
        item = await repo.get(chat_id=chat_id, item_id=item_id)
        if not item:
            await query.answer("Bulunamadı.", show_alert=True)
            return
        
        await query.answer("Görsel güncelleniyor...")
        
        # Yeni ürün bilgilerini çek
        try:
            product_info = await product_service.fetch_product_info(item.url)
            
            if product_info.image_url:
                # Database'i güncelle
                await repo.add(
                    chat_id=chat_id,
                    url=item.url,
                    baseline_price=product_info.price or item.baseline_price,
                    title=product_info.title or item.title,
                    image_url=product_info.image_url
                )
                
                # Yeni görseli gönder
                item = await repo.get(chat_id=chat_id, item_id=item_id)
                if query.message:
                    await query.message.delete()
                await _send_image_from_url(query, item, repo)
            else:
                await query.answer("Güncel görsel bulunamadı.", show_alert=True)
        except Exception as e:
            await query.answer(f"Hata: {str(e)[:50]}", show_alert=True)
        return

    await query.answer("Geçersiz işlem.", show_alert=True)


async def _send_image_from_url(query: CallbackQuery, item, repo: TrackingRepo) -> None:
    """URL'den görsel çek ve gönder, file_id'yi kaydet"""
    if not item.image_url:
        await query.answer("Görsel URL'i yok.", show_alert=True)
        return
    
    try:
        # Görseli indir
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(item.image_url)
            response.raise_for_status()
            image_data = response.content
        
        # Telegram'a gönder
        kb = InlineKeyboardBuilder()
        kb.button(text="🔄 Görseli Yenile", callback_data=TrackActionCb(action="refresh_image", item_id=item.id).pack())
        kb.button(text="⬅️ Geri", callback_data=TrackActionCb(action="back", item_id=item.id).pack())
        kb.adjust(1)
        
        caption = f"📦 {item.title or 'Ürün'}\n💰 {item.last_price:.2f} TL"
        
        sent_message = await query.message.answer_photo(
            photo=BufferedInputFile(image_data, filename="product.jpg"),
            caption=caption,
            reply_markup=kb.as_markup()
        )
        
        # File ID'yi kaydet (cache için)
        if sent_message.photo:
            file_id = sent_message.photo[-1].file_id
            await repo.set_telegram_file_id(
                chat_id=item.chat_id,
                item_id=item.id,
                file_id=file_id
            )
    
    except Exception as e:
        await query.answer(f"Görsel yüklenemedi: {str(e)[:50]}", show_alert=True)