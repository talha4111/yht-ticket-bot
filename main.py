import os
from dotenv import load_dotenv
load_dotenv()
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Hedef Bilgileri (Kendi hedeflerinize göre değiştirebilirsiniz)
# Sitenin tamamlama yapabilmesi için sadece kelimenin bir kısmını yazıyoruz
KALKIS = "izmit" 
VARIS = "yozgat"
TARIHLER = ["05.07.2026"] # Arayacağınız tüm tarihleri buraya ekleyebilirsiniz
HEDEF_SAATLER = [] # Sadece ilgilendiğiniz saatleri yazın. Tüm seferleri aramak için boş bırakın: []

# --- Telegram Ayarları ---
# Botunuzu Telegram'da @BotFather üzerinden oluşturup Token'ınızı buraya yazın.
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "BURAYA_TOKEN_GELECEK")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "BURAYA_CHAT_ID_GELECEK")
BEKLEME_SURESI = 60 # Saniye cinsinden kontrol aralığı (Örn: 60 = 1 dakika)

def send_telegram_message(message):
    """Bulunan bilet bilgisini Telegram üzerinden gönderir."""
    if TELEGRAM_TOKEN == "BURAYA_TOKEN_GELECEK":
        print(f"Bildirim (Telegram ayarlı değil): {message}")
        return
    
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def setup_driver():
    """Tarayıcıyı başlatır ve ayarlarını yapar."""
    print("Chrome tarayıcısı hazırlanıyor...")
    options = webdriver.ChromeOptions()
    
    # Arka planda sessizce çalışması için aktif edildi:
    options.add_argument('--headless=new') 
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')    
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3') # Gereksiz console loglarını gizler
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # Kırmızı hata loglarını gizler
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage') # Sunucularda çökmesini engeller
    options.add_argument('--disable-notifications')
    
    # Webdriver-manager indirmesi takıldığı için doğrudan sistemdeki yerel sürücüyü kullanıyoruz
    import os
    from selenium.webdriver.chrome.service import Service
    
    # Askıda kalan chromedriver işlemlerini temizleyelim ki yeni bağlantı takılmasın (Sadece Windows)
    if os.name == 'nt':
        try:
            os.system("taskkill /F /IM chromedriver.exe /T > nul 2>&1")
        except:
            pass

    # Sadece Linux (Sunucu) ortamındaysa Chromium ayarlarını kullan
    if os.name != 'nt': 
        options.binary_location = '/usr/bin/chromium-browser'
        if os.path.exists('/usr/bin/chromedriver'):
            service = Service('/usr/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
    else:
        # Windows (Kendi bilgisayarın) ortamı
        # Bağlantının takılmasını önlemek için sayfa yükleme zaman aşımı vb eklendi
        driver = webdriver.Chrome(options=options)
        
    driver.set_page_load_timeout(60)
    driver.maximize_window()
    return driver

def arama_yap(driver, hedef_tarih):
    """TCDD sayfasına gider ve bilet araması yapar."""
    print("TCDD E-Bilet sistemine bağlanılıyor...")
    # TCDD bilet sayfası (Yeni Sistem URL'si)
    driver.get("https://bilet.tcdd.gov.tr/")
    
    # Bekleme süresi
    wait = WebDriverWait(driver, 15)
    
    try:
        print("Sayfa yüklendi, kalkış ve varış bilgileri dolduruluyor...")
        
        # TCDD arama kutusu küçük 'i' ile başlayan kelimelerde sonuç çıkarmayabiliyor (Örn: izmit -> sonuç yok, İzmit -> sonuç var).
        # Bu yüzden kullanıcının girdiği değeri ilk harfi büyük olacak şekilde düzeltiyoruz.
        def tr_capitalize(text):
            if not text: return text
            # Sadece ilk harfi Türkçe kuralına göre büyütelim, geri kalanı küçük kalsın
            ilk_harf = text[0].replace('i', 'İ').replace('ı', 'I').upper()
            geri_kalan = text[1:].lower()
            return ilk_harf + geri_kalan

        kalkis_duzeltilmis = tr_capitalize(KALKIS)
        varis_duzeltilmis = tr_capitalize(VARIS)

        # --- KALKIŞ İSTASYONU ---
        kalkis_input = wait.until(EC.presence_of_element_located((By.ID, "fromTrainInput")))
        driver.execute_script("arguments[0].click();", kalkis_input)
        time.sleep(0.5)
        kalkis_input.send_keys(Keys.CONTROL + "a")
        kalkis_input.send_keys(Keys.BACKSPACE)
        kalkis_input.send_keys(kalkis_duzeltilmis)
        time.sleep(0.5)
        kalkis_input.send_keys(" ")
        time.sleep(0.2)
        kalkis_input.send_keys(Keys.BACKSPACE)
        print(f"Kalkış istasyonu ({kalkis_duzeltilmis}) aranıyor...")
        time.sleep(2)
        
        # TCDD dropdown listesi li değil, span.textLocation kullanıyor!
        kalkis_tr = KALKIS.replace('i', 'İ').replace('ı', 'I').upper()
        kalkis_secenek = wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//span[@class='textLocation'][contains(., '{kalkis_tr}')]")
        ))
        # Parent div'e tıklıyoruz çünkü span kendisi tıklanabilir olmayabilir
        kalkis_parent = kalkis_secenek.find_element(By.XPATH, "./ancestor::div[contains(@class, 'borderBottom')]")
        driver.execute_script("arguments[0].click();", kalkis_parent)
        print("Kalkış istasyonu seçildi.")
        time.sleep(1)
        
        # --- VARIŞ İSTASYONU ---
        varis_input = wait.until(EC.presence_of_element_located((By.ID, "toTrainInput")))
        driver.execute_script("arguments[0].click();", varis_input)
        time.sleep(0.5)
        varis_input.send_keys(Keys.CONTROL + "a")
        varis_input.send_keys(Keys.BACKSPACE)
        varis_input.send_keys(varis_duzeltilmis)
        time.sleep(0.5)
        varis_input.send_keys(" ")
        time.sleep(0.2)
        varis_input.send_keys(Keys.BACKSPACE)
        print(f"Varış istasyonu ({varis_duzeltilmis}) aranıyor...")
        time.sleep(2)
        
        varis_tr = VARIS.replace('i', 'İ').replace('ı', 'I').upper()
        varis_secenek = wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//span[@class='textLocation'][contains(., '{varis_tr}')]")
        ))
        varis_parent = varis_secenek.find_element(By.XPATH, "./ancestor::div[contains(@class, 'borderBottom')]")
        driver.execute_script("arguments[0].click();", varis_parent)
        print("Varış istasyonu seçildi.")
        
        # --- TARİH ---
        print(f"\n--- {hedef_tarih} Tarihi İçin Bilet Aranıyor ---")
        try:
            # 1. Takvimi açmak için tarih kutusuna tıkla
            tarih_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='GidişTarihi']")))
            driver.execute_script("arguments[0].click();", tarih_input)
            time.sleep(1)
            
            # 2. Tarih parçalarını al (Örn: "03.06.2026" -> gün=3, ay=6, yıl=2026)
            tarih_parcalari = hedef_tarih.split('.')
            hedef_gun = str(int(tarih_parcalari[0]))
            hedef_ay = int(tarih_parcalari[1])
            hedef_yil = int(tarih_parcalari[2])
            
            # 3. Takvimin gösterdiği ay ve yılı kontrol edip doğru aya ilerle
            # TCDD takviminde aylar genellikle "Mayıs 2026" veya "May 2026" şeklinde gösterilir
            ay_isimleri = {1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 
                          6: 'Haziran', 7: 'Temmuz', 8: 'Ağustos', 9: 'Eylül', 
                          10: 'Ekim', 11: 'Kasım', 12: 'Aralık'}
            
            # Takvimde en fazla 12 kez ileri butonuna basarak doğru aya ulaş
            for _ in range(12):
                # Takvim başlığından mevcut ay bilgisini oku
                try:
                    takvim_basligi = driver.find_element(By.CSS_SELECTOR, ".daterangepicker .month, .drp-calendar .month, th.month").text
                except:
                    takvim_basligi = ""
                
                # Hedef ay/yıl başlıkta varsa doğru aydayız
                hedef_ay_adi = ay_isimleri.get(hedef_ay, '')
                if hedef_ay_adi in takvim_basligi and str(hedef_yil) in takvim_basligi:
                    break
                
                # Değilse ileri butonuna bas
                try:
                    ileri_btn = driver.find_element(By.CSS_SELECTOR, ".daterangepicker .next, .drp-calendar .next, th.next")
                    driver.execute_script("arguments[0].click();", ileri_btn)
                    time.sleep(0.5)
                except:
                    break
            
            # 4. Doğru aydayız, şimdi hedef güne tıkla
            # data-date özniteliği ile tam doğru günü seçiyoruz (Örn: 2026-05-29)
            hedef_data_date = f"{hedef_yil}-{hedef_ay:02d}-{int(hedef_gun):02d}"
            driver.execute_script(f"""
                var td = document.querySelector('td[data-date="{hedef_data_date}"]');
                if (td) {{
                    td.click();
                }} else {{
                    // Fallback: eski yöntemi dene
                    var cells = document.querySelectorAll('td:not(.off)');
                    for (var i=0; i<cells.length; i++) {{
                        if (cells[i].innerText.trim() === '{hedef_gun}') {{
                            cells[i].click();
                            break;
                        }}
                    }}
                }}
            """)
            print(f"Takvimden {hedef_data_date} ({hedef_gun}. gün) başarıyla seçildi.")
            time.sleep(1)
        except Exception as e:
            print(f"Tarih girilirken hata oluştu: {e}")
        
        # --- ARA BUTONU ---
        print("Bilgiler girildi, 'Ara' butonuna tıklanıyor...")
        time.sleep(1) # Formun algılanması için çok kısa bekleme
        ara_btn = wait.until(EC.presence_of_element_located((By.ID, "searchSeferButton")))
        driver.execute_script("arguments[0].click();", ara_btn)
        
        print("Sonuç sayfası bekleniyor...")
        # Sonuçların yüklendiğini kesin olarak anlamak için URL'nin değişmesini bekliyoruz
        wait.until(EC.url_contains("sefer"))
        print("Sonuç sayfası yüklendi, biletlerin listelenmesi bekleniyor...")
        time.sleep(12) # Biletlerin yüklenmesi için bekleme süresini artırdık (TCDD yavaş yüklenebilir)
        
        seferler = driver.find_elements(By.CSS_SELECTOR, "button[id^='gidis']")
        print(f"Toplam {len(seferler)} sefer bulundu. Analiz ediliyor...")
        
        # Eğer sefer bulunamadıysa (DOM değiştiyse) sayfa kaynağını kaydet ki analiz edebilelim
        if len(seferler) == 0:
            with open("sefer_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Sayfa kaynağı 'sefer_source.html' olarak kaydedildi. Analiz için bekleniyor...")
        
        bulundu = False
        for sefer in seferler:
            try:
                # Saat bilgisini çek (Kalkış saati her zaman ilk time etiketidir)
                saat_etiketleri = sefer.find_elements(By.TAG_NAME, "time")
                if len(saat_etiketleri) > 0:
                    saat = saat_etiketleri[0].text.strip()
                else:
                    saat = "Saat Bulunamadı"
                
                # Kullanıcı saati yanlışlıkla '20.50' gibi noktalı girerse diye formatı düzeltiyoruz
                duzeltilmis_hedefler = [s.replace('.', ':') for s in HEDEF_SAATLER]
                
                # Belirli saatler hedeflenmişse ve bu sefer onlardan biri değilse, hiç açmadan atla
                if duzeltilmis_hedefler and saat.replace('.', ':') not in duzeltilmis_hedefler:
                    continue
                
                # Seferi ekranda görünür yapıp tıklıyoruz (JS click kullanıyoruz ki loader vs engellemesin)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sefer)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", sefer)
                time.sleep(2) # Panelin açılması ve vagon tiplerinin yüklenmesi için bekle
                
                # Açılan bilet butonlarını bul (TCDD'nin yeni sisteminde genelde butonların içinde fiyat ve bilet tipi yazar)
                # O an ekranda GÖRÜNÜR olan ve içinde TL (₺) simgesi geçen butonları arıyoruz
                vagon_butonlari = driver.find_elements(By.XPATH, "//button[contains(., '₺')]")
                
                for vagon in vagon_butonlari:
                    if not vagon.is_displayed():
                        continue
                        
                    vagon_text = vagon.text
                    if not vagon_text: continue
                    
                    import re
                    
                    # TEKERLEKLİ SANDALYE veya ana kart yazılarını atla (çok uzun metinler genelde ana karttır)
                    if 'TEKERLEKLİ SANDALYE' in vagon_text.upper():
                        continue
                    
                    # Yöntem 1: Eski format - EKONOMİ/STANDART/PULMAN (N)
                    match = re.search(r'(EKONOMİ|STANDART|PULMAN|Ekonomi|Standart|Pulman).*?\((\d+)\)', vagon_text, re.DOTALL)
                    
                    # Yöntem 2: Yeni format - ₺Fiyat\n(N)  
                    if not match:
                        match2 = re.search(r'₺[\d.,]+\s*\n?\s*\((\d+)\)', vagon_text)
                        if match2:
                            tip = "BİLET"
                            bos_koltuk = int(match2.group(1))
                            match = True  # Flag olarak kullan
                        else:
                            match = None
                    
                    if match and match is not True:
                        tip = match.group(1).upper()
                        bos_koltuk = int(match.group(2))
                    
                    if match:
                        print(f"Sefer: {saat} | Tip: {tip} | Boş Koltuk: {bos_koltuk}")
                        
                        if bos_koltuk > 0:
                            mesaj = f"🚀 BİLET BULUNDU!\n\n📅 Tarih: {hedef_tarih}\n🕒 Saat: {saat}\n💺 Boş Yer: {bos_koltuk}\n📍 {tip} Sınıfı\n🧭 {KALKIS} -> {VARIS}\n\nHemen al: https://bilet.tcdd.gov.tr/"
                            send_telegram_message(mesaj)
                            bulundu = True
                            
                # İşimiz bitince paneli geri kapatıyoruz
                driver.execute_script("arguments[0].click();", sefer)
                time.sleep(0.5)
                
                
            except Exception as e:
                continue
        
        if not bulundu:
            print("Maalesef şu an uygun boş koltuk bulunmuyor.")

    except Exception as e:
        import traceback
        print(f"Bir hata oluştu:\n{traceback.format_exc()}")

if __name__ == "__main__":
    import sys
    import codecs
    if sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        except Exception:
            pass

    print(f"🚀 YHT Bilet Botu Başlatıldı! (Kontrol Aralığı: {BEKLEME_SURESI} saniye)")
    print(f"Rota: {KALKIS} -> {VARIS} | Tarihler: {', '.join(TARIHLER)}")
    
    while True:
        tarayici = None
        try:
            tarayici = setup_driver()
            for t in TARIHLER:
                arama_yap(tarayici, t)
                time.sleep(3) # Diğer tarihe geçmeden önce çok kısa bir bekleme
        except Exception as main_e:
            print(f"Beklenmedik bir hata oluştu: {main_e}")
        finally:
            if tarayici:
                print("Tarayıcı kapatılıyor...")
                tarayici.quit()
        
        print(f"\n{time.strftime('%H:%M:%S')} - Bekleme moduna geçiliyor ({BEKLEME_SURESI} sn)...")
        time.sleep(BEKLEME_SURESI)
