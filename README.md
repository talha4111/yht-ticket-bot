<div align="center">
  <h1>🚄 TCDD YHT Ticket Automation & Notification Engine</h1>
  <p><strong>Python & Selenium WebDriver Tabanlı 7/24 Otonom Yüksek Hızlı Tren Bilet Tarayıcı ve Telegram Bildirim Sistemi</strong></p>
  
  [![Python Version](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Selenium](https://img.shields.io/badge/Selenium-WebDriver-43B02A?style=for-the-badge&logo=selenium&logoColor=white)](https://www.selenium.dev/)
  [![Telegram API](https://img.shields.io/badge/Telegram-Bot_API-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots/api)
  [![Linux VPS](https://img.shields.io/badge/Deploy-Paramiko_SSH-FCC624?style=for-the-badge&logo=linux&logoColor=black)]()
</div>

<br>

## 📖 Proje Hakkında
**TCDD YHT Ticket Bot**, TCDD Taşımacılık e-bilet platformu üzerinde belirlenen güzergâh, tarih ve saat aralıklarındaki Yüksek Hızlı Tren (YHT) seferlerini 7/24 otonom olarak tarayan, boş koltuk (Ekonomi / Business) açıldığı anda **Telegram Bot API** üzerinden gerçek zamanlı bildirim gönderen bir web otomasyon ve izleme sistemidir.

Dinamik SPA (Single Page Application) DOM yapısına uyum sağlayan açık bekleme (`WebDriverWait` / `expected_conditions`), XPath/CSS seçicileri, Regex tabanlı koltuk ayrıştırıcı ve Linux VPS sunucularına tek komutla uzaktan dağıtım (`Paramiko SSH/SFTP`) altyapısına sahiptir.

---

## ✨ Temel Özellikler
- 🔄 **7/24 Kesintisiz Headless Tarama:** Sunucu ve masaüstü ortamlarında arka planda (`--headless=new`, `--no-sandbox`, `--disable-dev-shm-usage`) düşük bellek ve CPU tüketimiyle çalışır.
- 🎯 **Dinamik DOM & Autocomplete Yönetimi:** TCDD'nin dinamik istasyon otomatik tamamlama ve takvim bileşenlerini `WebDriverWait` ve JavaScript yürütücüleri ile hatasız simüle eder.
- 🔍 **Regex Tabanlı Kontenjan Ayrıştırma:** Sefer vagon tiplerini (Ekonomi, Business, Tekerlekli Sandalye hariç gerçek boş koltuklar) düzenli ifadeler (`re`) ile analiz ederek yanlış pozitif bildirimleri engeller.
- 📲 **Anlık Telegram Uyarıları:** Boş koltuk tespit edildiği anda tarih, saat, boş koltuk sayısı ve sınıf bilgisiyle birlikte doğrudan Telegram üzerinden bildirim tetikler.
- ☁️ **Otonom VPS Dağıtımı (`deploy.py` & `update.py`):** `Paramiko` SSH/SFTP istemcisi ile uzak Linux sunucusuna otomatik paket kurulumu, sanal ortam (`venv`) yapılandırması ve `screen` oturumu yönetimi sağlar.
- 🔐 **Güvenli Yapılandırma:** Tüm hassas anahtarlar ve sunucu bilgileri `.env` ortam değişkenleri üzerinden izole edilmiştir.

---

## 🛠️ Kurulum ve Kullanım

### 1. Repoyu Klonlayın
```bash
git clone https://github.com/talha4111/yht-ticket-bot.git
cd yht-ticket-bot
```

### 2. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 3. Ortam Değişkenlerini Yapılandırın (`.env`)
`.env.example` dosyasını `.env` olarak kopyalayın ve kendi bilgilerinizi girin:
```bash
cp .env.example .env
```
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
YHT_KALKIS=izmit
YHT_VARIS=ankara
YHT_TARIHLER=05.07.2026
YHT_BEKLEME_SURESI=60
```

### 4. Uygulamayı Başlatın
```bash
python main.py
```

---

## 📂 Mimari Yapı
```text
yht-ticket-bot/
├── main.py            # Çekirdek Selenium tarama motoru, Regex koltuk analizi ve Telegram bildirimcisi
├── deploy.py          # Paramiko tabanlı sıfırdan Linux VPS kurulum ve servis başlatma betiği
├── update.py          # Çalışan uzak sunucudaki botu kesintisiz güncelleme betiği
├── debug.py           # Sayfa DOM yapısını doğrulama ve tanılama aracı
├── .env.example       # Örnek ortam değişkenleri şablonu
└── requirements.txt   # Python paket bağımlılıkları
```

---

## 👨‍💻 Geliştirici
**Talha Gürler** — [GitHub (@talha4111)](https://github.com/talha4111)
