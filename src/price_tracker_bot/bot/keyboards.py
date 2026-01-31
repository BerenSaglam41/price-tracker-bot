from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callbacks import TrackActionCb

def tracking_item_kb(item_id: int, is_active: bool, has_image: bool = False) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()

    if is_active:
        b.button(text="⏸ Durdur", callback_data=TrackActionCb(action="pause", item_id=item_id).pack())
    else:
        b.button(text="▶️ Devam", callback_data=TrackActionCb(action="resume", item_id=item_id).pack())

    b.button(text="🗑 Sil", callback_data=TrackActionCb(action="remove", item_id=item_id).pack())
    
    # Görsel butonu - sadece görseli varsa göster
    if has_image:
        b.button(text="🖼️ Görsel", callback_data=TrackActionCb(action="show_image", item_id=item_id).pack())
    
    b.button(text="🎯 Eşik", callback_data=TrackActionCb(action="threshold_menu", item_id=item_id).pack())

    b.adjust(2, 2) if has_image else b.adjust(2, 1)
    return b.as_markup()

def after_add_kb(item_id: int, has_image: bool = False) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    
    # Görsel butonu - eğer görsel varsa
    if has_image:
        b.button(text="🖼️ Görseli Göster", callback_data=TrackActionCb(action="show_image", item_id=item_id).pack())
    
    b.button(text="🎯 Eşik ayarla", callback_data=TrackActionCb(action="threshold_menu", item_id=item_id).pack())
    
    b.adjust(2) if has_image else b.adjust(1)
    return b.as_markup()

def threshold_menu_kb(item_id: int) -> InlineKeyboardMarkup:
    """
    Hızlı seçim menüsü: 0 / 3 / 5 / 10 / 15
    0 => her düşüşte bildir
    """
    b = InlineKeyboardBuilder()
    for pct in (0, 3, 5, 10, 15):
        label = "0% (her düşüş)" if pct == 0 else f"%{pct}+ düşüş"
        b.button(
            text=label,
            callback_data=TrackActionCb(action="threshold_set", item_id=item_id, value=str(pct)).pack(),
        )

    # Geri butonu
    b.button(text="⬅️ Geri", callback_data=TrackActionCb(action="back", item_id=item_id).pack())
    b.button(text="🧹 Kapat", callback_data=TrackActionCb(action="close", item_id=item_id).pack())

    b.adjust(1, 2, 2, 1)  # 1 + 2 + 2 + 1
    return b.as_markup()