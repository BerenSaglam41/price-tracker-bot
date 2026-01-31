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
# WEBHOOK_URL boş bırakın - local'de polling kullanılır
```

5. **Database'i hazırlayın:**
```bash
python init_db.py
```

6. **Botu başlatın:**
```bash
./run.sh
# veya
python -m src.price_tracker_bot.main
```

**Not:** Local geliştirmede WEBHOOK_URL boş kalır, bot otomatik olarak polling modunu kullanır.

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

## 🚀 Cloud'a Deploy (Ücretsiz)

### Render.com (Önerilen)

#### Adım 1: PostgreSQL Database Oluştur
1. [Render.com](https://render.com)'a giriş yap
2. "New +" → "PostgreSQL" seç
3. Database adı: `price-tracker-db`
4. Plan: Free
5. Create Database

#### Adım 2: Web Service Oluştur
1. "New +" → "Web Service" seç
2. Bu GitHub repo'yu bağla
3. Ayarlar:
   - **Name**: `price-tracker-bot`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m src.price_tracker_bot.main`

#### Adım 3: Environment Variables
Dashboard'da Environment variables ekle:
- `BOT_TOKEN`: Telegram bot token'ın (BotFather'dan)
- `WEBHOOK_URL`: `https://YOUR-APP-NAME.onrender.com` (App URL'inizi buraya yazın)
- `DATABASE_URL`: PostgreSQL database'den otomatik bağlanacak

#### Adım 4: Deploy Et!
- "Create Web Service" butonuna tıkla
- İlk deploy ~5 dakika sürer
- Bot otomatik olarak database tablolarını oluşturacak
- Health check: `https://YOUR-APP-NAME.onrender.com/health`

**Önemli Notlar:**
- ✅ Webhook modu kullanıldığı için Render'da düzgün çalışır
- ✅ Database tabloları otomatik oluşturulur
- ✅ Ücretsiz tier ile 7/24 çalışır
- ⚠️ Free tier 15 dakika inaktivite sonrası uyur, webhook gelince uyanır

### Alternatifler

- **fly.io**: Telegram botlar için popüler
- **Railway**: Kolay deploy, $5 ücretsiz credit
- **Koyeb**: Kolay deploy

## 👤 Geliştirici

Mustafa Beren - Öğrenci Projesi

---

⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!
