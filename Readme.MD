# 🛍️ Trendyol Fiyat Takip Botu

Trendyol ürünlerinin fiyatlarını otomatik takip eden Telegram botu. Her 5 dakikada bir fiyatları kontrol edip düşünce bildirim gönderir.

## 📌 Özellikler

- ✅ Trendyol ürün linklerini takip etme
- ✅ Otomatik fiyat kontrolü (her 5 dakika)
- ✅ Fiyat düşünce bildirim
- ✅ Ürün görselleri
- ✅ Kısa linkler (ty.gl) desteği
- ✅ Eşik fiyat belirleme
- ✅ PostgreSQL/SQLite desteği

## 🚀 Kurulum

### Gereksinimler
- Python 3.10+
- pip

### Adımlar

1. **Virtual environment oluşturun:**
```bash
python -m venv .venv
source .venv/bin/activate
```

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Bot token alın:**
- Telegram'da @BotFather'ı açın
- /newbot komutu ile bot oluşturun
- Token'ı kopyalayın

4. **.env dosyası oluşturun:**
```bash
cp .env.example .env
```

.env dosyasını düzenleyin:
```
BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite+aiosqlite:///./price_tracker.db
```

5. **Botu başlatın:**
```bash
./run.sh
```

## 📱 Kullanım

### Komutlar
- `/start` - Botu başlat
- `/add <link>` - Ürün ekle
- `/list` - Ürünleri listele

### Örnek
```
/add https://www.trendyol.com/urun-p-12345
/add https://ty.gl/xxxxx
/list
```

## 🗂️ Proje Yapısı

```
price-tracker-bot/
├── src/
│   └── price_tracker_bot/
│       ├── main.py              # Ana uygulama
│       ├── config.py            # Yapılandırma
│       ├── bot/
│       │   ├── handlers/        # Komut handler'ları
│       │   ├── keyboards.py     # Inline klavyeler
│       │   └── middlewares/     # Middleware'ler
│       ├── db/
│       │   ├── models.py        # Veritabanı modelleri
│       │   └── repo/            # Repository pattern
│       └── services/
│           └── product_enrichment.py  # Trendyol scraper
├── requirements.txt
└── README.md
```

## 🛠️ Teknolojiler

- **aiogram 3.x** - Telegram Bot framework
- **SQLAlchemy 2.x** - ORM
- **APScheduler 3.x** - Otomatik fiyat kontrolü
- **aiosqlite / asyncpg** - SQLite / PostgreSQL
- **httpx** - HTTP client
- **BeautifulSoup4** - HTML parsing

## 🚀 Railway'e Deploy

1. [Railway.app](https://railway.app)'e giriş yap
2. "New Project" → "Deploy from GitHub repo" seç
3. Bu repo'yu seç
4. "Add PostgreSQL" database ekle
5. Environment variables ekle:
   - `BOT_TOKEN`: Telegram bot token'ın
6. Deploy et!

Railway otomatik olarak `DATABASE_URL` ekleyecek ve bot 7/24 çalışacak.

## 👤 Geliştirici

Mustafa Beren - Öğrenci Projesi

---

⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!
