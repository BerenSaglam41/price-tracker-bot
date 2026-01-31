from __future__ import annotations
from aiogram.filters.callback_data import CallbackData

class TrackActionCb(CallbackData, prefix="trk"):
    action: str  # "pause" | "resume" | "remove" | "threshold_menu" | "threshold_set" | "back" | "close" | "show_image" | "refresh_image"
    item_id: int
    value: str | None = None  