from aiogram import Router
from aiogram.filters import CommandStart,Command
from aiogram.types import Message

router = Router()

HELP_TEXT = (
    "📌 Fiyat Takip Botu\n\n"
    "Komutlar:\n"
    "/add <url>            - ürünü takibe al (mevcut fiyat referans alınır)\n"
    "/list                 - takiplerini listele\n"
    "/remove <id>          - takip sil\n"
    "/pause <id>           - takibi durdur\n"
    "/resume <id>          - takibi devam ettir\n"
    "/help                 - yardım\n\n"
    "Örnek:\n"
    "/add https://example.com/urun\n"
)

@router.message(CommandStart())
async def on_start(message: Message) -> None:
    await message.answer(
        "Fiyat Takip Botuna Hoşgeldiniz!\n\n" + HELP_TEXT
    )
@router.message(Command("help"))
async def on_help(message: Message) -> None:
    await message.answer(HELP_TEXT)