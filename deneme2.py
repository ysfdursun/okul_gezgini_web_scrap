# import requests
# import pandas as pd
# from concurrent.futures import ThreadPoolExecutor
# import time
# import os

# # --- Ayarlar ---
# DOSYA_YOLU = "KurumlarınTamListesi.xlsx"
# PAKET_BOYUTU = 500  # Her seferde kaç satır işlenecek
# MOLA_SURESI = 300    # Paket bitince kaç saniye beklenecek (300sn = 5dk)
# MAX_WORKERS = 15     # Aynı anda kaç site sorgulanacak (Ban riskine karşı 15 ideal)

# HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# }

# # --- Fonksiyonlar (Öncekiyle aynı) ---
# def convert_to_english(text):
#     if not isinstance(text, str): return ""
#     translations = str.maketrans("çğışıöü", "cgisiou")
#     return text.lower().translate(translations)

# # def get_clean_main_name(full_name):
# #     words = [convert_to_english(w) for w in str(full_name).split()]
# #     if not words: return ""
# #     if words[0] == "ozel": words = words[1:]
# #     if len(words) > 1: words = words[:-1]
# #     return "".join(words)

# def get_clean_main_name(full_name):
#     # 1. Temizlenecek Kelimeler (Okul türleri ve İller)
#     yasakli_kelimeler = {
#         "ozel", "anadolu", "fen", "lisesi", "ortaokulu", "ilkokulu", 
#         "koleji", "okullari", "etut", "merkezi", "kursu", "egitim", "mesleki", "teknik",
#         # Türkiye'nin 81 ili (Küçük harf ve İngilizce karakter formatında)
#         "adana", "adiyaman", "afyonkarahisar", "agri", "amasya", "ankara", "antalya", "artvin",
#         "aydin", "balikesir", "bilecik", "bingol", "bitlis", "bolu", "burdur", "bursa", "canakkale",
#         "cankiri", "corum", "denizli", "diyarbakir", "edirne", "elazig", "erzincan", "erzurum",
#         "eskisehir", "gaziantep", "giresun", "gumushane", "hakkari", "hatay", "isparta", "mersin",
#         "istanbul", "izmir", "kars", "kastamonu", "kayseri", "kirklareli", "kirsehir", "kocaeli",
#         "konya", "kutahya", "malatya", "manisa", "kahramanmaras", "mardin", "mugla", "mus",
#         "nevsehir", "nigde", "ordu", "rize", "sakarya", "samsun", "siirt", "sinop", "sivas",
#         "tekirdag", "tokat", "trabzon", "tunceli", "sanliurfa", "usak", "van", "yozgat", "zonguldak",
#         "aksaray", "bayburt", "karaman", "kirikkale", "batman", "sirnak", "bartin", "ardahan",
#         "igdir", "yalova", "karabuk", "kilis", "osmaniye", "duzce"
#     }

#     # 2. Kelimelere ayır ve İngilizce karaktere çevir
#     words = [convert_to_english(w) for w in str(full_name).split()]
    
#     # 3. Yasaklı kelimeleri listeden at
#     # Eğer kelime yasaklı listede yoksa tutulur
#     clean_words = [w for w in words if w not in yasakli_kelimeler]
    
#     # 4. Eğer her şey silindiyse (örn: "Özel İstanbul Anadolu Lisesi" -> hepsi yasaklı olabilir)
#     # Bu durumda orijinal listedeki anlamlı bir kelimeyi (örn: 1. index) geri getir
#     if not clean_words:
#         return "".join(words[:2]) # En azından ilk iki kelimeyi birleştir (ozelistanbul gibi)

#     # 5. Kalan kelimeleri birleştir (örn: ["deniz", "yildizi"] -> "denizyildizi")
#     return "".join(clean_words)
# def generate_url_variants(full_name):
#     main_name = get_clean_main_name(full_name)
#     if not main_name: return []
#     base_variants = [f"{main_name}okullari", f"ozel{main_name}okullari", f"{main_name}koleji", 
#                      f"{main_name}-okullari", f"ozel-{main_name}-okullari", f"{main_name}-koleji"]
#     uzantilar = [".com", ".com.tr", ".k12.tr"]
#     return [f"http://www.{base}{ext}" for base in base_variants for ext in uzantilar]

# def find_active_website(kurum_adi):
#     if pd.isna(kurum_adi) or kurum_adi == "": return "İsim Yok"
#     urls = generate_url_variants(kurum_adi)
#     for url in urls:
#         try:
#             response = requests.head(url, timeout=1.5, headers=HEADERS, allow_redirects=True)
#             if response.status_code < 400:
#                 return url
#         except Exception as e:
#             print(f"Hata: {url} -> {e}")
#             continue
#     return "Bulunamadı"

# # --- Ana İşleyicisi ---

# def ana_isleyici():
#     # Excel'i oku
#     df = pd.read_excel(DOSYA_YOLU)
    
#     if 'Web Sitesi' not in df.columns:
#         df['Web Sitesi'] = None

#     # --- MANUEL AYARLAR ---
#     baslangic = 1000  # Kaçıncı satırdan başlasın?
#     bitis = 1010     # Kaçıncı satıra kadar gitsin? (10 dahil değil)
#     # ----------------------

#     print(f"\n[>] {baslangic}. satır ile {bitis}. satır arası işleniyor...")
    
#     # Sadece belirlediğin aralığı seçiyoruz
#     alt_df = df.iloc[baslangic:bitis]
    
#     # Seçilen aralığı multithreading ile tara
#     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#         sonuclar = list(executor.map(find_active_website, alt_df['Kurum Adı']))
    
#     # Sonuçları ana DataFrame'de ilgili satırlara yerleştir
#     df.loc[baslangic:bitis-1, 'Web Sitesi'] = sonuclar
    
#     # Dosyayı kaydet
#     df.to_excel(DOSYA_YOLU, index=False)
#     print(f"[+] {baslangic}-{bitis} arası başarıyla kaydedildi.")

#     # for i in range(0, toplam_satir, PAKET_BOYUTU):
#     #     # bitis = min(i + PAKET_BOYUTU, toplam_satir)
#     #     bitis=10
#     #     print(f"\n[>] {i} - {bitis} arası satırlar işleniyor...")
        
#     #     # Sadece web sitesi henüz bulunmamış (None) olanları işle
#     #     # Bu sayede kod durursa tekrar çalıştırdığında kaldığı yerden devam eder
#     #     alt_df = df.iloc[i:bitis]
        
#     #     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#     #         sonuclar = list(executor.map(find_active_website, alt_df['Kurum Adı']))
        
#     #     # Sonuçları ana DataFrame'e yaz
#     #     df.loc[i:bitis-1, 'Web Sitesi'] = sonuclar
        
#     #     # Her paketten sonra dosyayı kaydet (Güvenlik önlemi)
#     #     df.to_excel(DOSYA_YOLU, index=False)
#     #     print(f"[+] {bitis} satıra kadar olan kısım kaydedildi.")
        
#     #     # # Son paket değilse mola ver
#     #     # if bitis < toplam_satir:
#     #     #     print(f"[!] IP Ban riskine karşı {MOLA_SURESI/60} dakika mola veriliyor...")
#     #     #     time.sleep(MOLA_SURESI)

#     # print("\n[FINISH] Tüm liste başarıyla tarandı ve güncellendi!")

# if __name__ == "__main__":
#     ana_isleyici()


# # # --- Tekli Test Bölümü ---
# # if __name__ == "__main__":
#     test_okul = "ÖZEL EMRE ORTAOKULU"
    
#     print(f"Test Edilen İsim: {test_okul}")
    
#     # 1. Adım: İsmin nasıl temizlendiğini gör
#     temiz_isim = get_clean_main_name(test_okul)
#     print(f"Üretilen Kök İsim: {temiz_isim}") 
#     # Beklenen çıktı: "bogazici" (ozel, kahramanmaras, fen, lisesi kelimeleri atılmalı)
    
#     # 2. Adım: Üretilen varyasyonları gör
#     varyasyonlar = generate_url_variants(test_okul)
#     print(f"Denecek URL Sayısı: {len(varyasyonlar)}")
    
#     # 3. Adım: Aktif siteyi bul (Bu işlem internet hızına göre birkaç saniye sürebilir)
#     sonuc = find_active_website(test_okul)
#     print(f"\nFinal Sonucu: {sonuc}")


import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time

# --- AYARLAR ---
DOSYA_YOLU = "KurumlarınTamListesi.xlsx"
MAX_WORKERS = 5  # Hız limiti
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# --- YARDIMCI FONKSİYONLAR ---
def convert_to_english(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    translations = str.maketrans("çğışıöü", "cgisiou")
    return text.translate(translations)

def get_clean_main_name(full_name):
    yasakli_kelimeler = {
        "ozel", "anadolu", "fen", "lisesi", "ortaokulu", "ilkokulu", "anaokulu",
        "koleji", "okullari", "etut", "merkezi", "kursu", "egitim", "mesleki", "teknik",
        "adana", "adiyaman", "afyonkarahisar", "agri", "amasya", "ankara", "antalya", "artvin",
        "aydin", "balikesir", "bilecik", "bingol", "bitlis", "bolu", "burdur", "bursa", "canakkale",
        "cankiri", "corum", "denizli", "diyarbakir", "edirne", "elazig", "erzincan", "erzurum",
        "eskisehir", "gaziantep", "giresun", "gumushane", "hakkari", "hatay", "isparta", "mersin",
        "istanbul", "izmir", "kars", "kastamonu", "kayseri", "kirklareli", "kirsehir", "kocaeli",
        "konya", "kutahya", "malatya", "manisa", "kahramanmaras", "mardin", "mugla", "mus",
        "nevsehir", "nigde", "ordu", "rize", "sakarya", "samsun", "siirt", "sinop", "sivas",
        "tekirdag", "tokat", "trabzon", "tunceli", "sanliurfa", "usak", "van", "yozgat", "zonguldak",
        "aksaray", "bayburt", "karaman", "kirikkale", "batman", "sirnak", "bartin", "ardahan",
        "igdir", "yalova", "karabuk", "kilis", "osmaniye", "duzce"
    }
    
    words = [convert_to_english(w) for w in str(full_name).split()]
    clean_words = [w for w in words if w not in yasakli_kelimeler and len(w) > 2]
    
    if not clean_words:
        return "".join(words[:2])
    return "".join(clean_words)

def generate_url_variants(full_name):
    main_name = get_clean_main_name(full_name)
    if not main_name: return []
    
    base_variants = [
        f"{main_name}okullari", f"ozel{main_name}okullari", f"{main_name}koleji", 
        f"{main_name}-okullari", f"ozel-{main_name}-okullari", f"{main_name}-koleji"
    ]
    uzantilar = [".com", ".com.tr", ".k12.tr"]
    return [f"http://www.{base}{ext}" for base in base_variants for ext in uzantilar]

def find_active_website(kurum_adi):
    if pd.isna(kurum_adi) or str(kurum_adi).strip() == "" or str(kurum_adi).lower() == "nan":
        return "İsim Yok"
    
    urls = generate_url_variants(kurum_adi)
    for url in urls:
        try:
            response = requests.head(url, timeout=2.0, headers=HEADERS, allow_redirects=True)
            if response.status_code < 400:
                return url
        except:
            continue
    return "Bulunamadı"

# --- ANA İŞLEYİCİ ---
def ana_isleyici():
    try:
        df = pd.read_excel(DOSYA_YOLU)
        
        # HATA DÜZELTME: Sütun adlarını güvenli bir şekilde temizle
        # Eğer sütun ismi string değilse olduğu gibi bırakır
        df.columns = [str(c).strip() if isinstance(c, str) else c for c in df.columns]
        
        if 'Web Sitesi' not in df.columns:
            df['Web Sitesi'] = None

        # --- MANUEL ARALIK AYARI ---
        baslangic = 1010
        bitis = 1100 
        # ---------------------------

        print(f"\n[>] {baslangic} - {bitis} arası taranıyor...")
        
        alt_df = df.iloc[baslangic:bitis].copy()
        kurum_listesi = alt_df['Kurum Adı'].astype(str).tolist()
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            sonuclar = list(executor.map(find_active_website, kurum_listesi))
        
        df.iloc[baslangic:bitis, df.columns.get_loc('Web Sitesi')] = sonuclar
        
        df.to_excel(DOSYA_YOLU, index=False)
        print(f"[+] {baslangic}-{bitis} arası başarıyla kaydedildi.")

    except PermissionError:
        print("HATA: Lütfen Excel dosyasını kapatıp tekrar deneyin!")
    except KeyError:
        print("HATA: Excel'de 'Kurum Adı' sütunu bulunamadı. Sütun isimlerini kontrol edin.")
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")

if __name__ == "__main__":
    ana_isleyici()








import pandas as pd
import socket
from concurrent.futures import ThreadPoolExecutor
import re
# --- AYARLAR ---
DOSYA_YOLU = "KurumlarınTamListesi.xlsx"
MAX_WORKERS = 20   # DNS çok hızlı olduğu için artırabiliriz

# ---------------- TEXT TEMİZLEME ----------------
def convert_to_english(text):
    if not isinstance(text, str):
        return ""
    translations = str.maketrans("çğışıöüÇĞİŞÖÜ", "cgisiouCGISOU")
    return text.lower().translate(translations)

def normalize_word(text):
    text = convert_to_english(text)
    # harf ve sayı dışındaki her şeyi sil
    text = re.sub(r"[^a-z0-9]", "", text)
    return text

def load_ilceler_from_excel(path):
    df = pd.read_csv(path)

    ilceler = set()

    for ilce in df["ilce_yeni"].dropna():
        ilceler.add(normalize_word(ilce))

    return ilceler

def load_mahalleler_from_excel(path):
    df = pd.read_csv(path)

    ilceler = set()

    for ilce in df["mahalle_temiz"].dropna():
        ilceler.add(normalize_word(ilce))

    return ilceler


# Excel dosyan (ilçelerin olduğu)
ILCELER = load_ilceler_from_excel("temiz_ingilizce_ilceler.csv")
# MAHALLELER = load_mahalleler_from_excel("temiz_mahalleler.csv")
YASAKLI_KELIMELER = {
        "ozel", "anadolu", "fen", "lisesi", "ortaokulu", "ilkokulu", "anaokulu",
        "koleji", "okullari", "etut", "merkezi", "kursu", "egitim", "mesleki", "teknik",
        "adana", "adiyaman", "afyonkarahisar", "agri", "amasya", "ankara", "antalya", "artvin",
        "aydin", "balikesir", "bilecik", "bingol", "bitlis", "bolu", "burdur", "bursa", "canakkale",
        "cankiri", "corum", "denizli", "diyarbakir", "edirne", "elazig", "erzincan", "erzurum",
        "eskisehir", "gaziantep", "giresun", "gumushane", "hakkari", "hatay", "isparta", "mersin",
        "istanbul", "izmir", "kars", "kastamonu", "kayseri", "kirklareli", "kirsehir", "kocaeli",
        "konya", "kutahya", "malatya", "manisa", "kahramanmaras", "mardin", "mugla", "mus",
        "nevsehir", "nigde", "ordu", "rize", "sakarya", "samsun", "siirt", "sinop", "sivas",
        "tekirdag", "tokat", "trabzon", "tunceli", "sanliurfa", "usak", "van", "yozgat", "zonguldak",
        "aksaray", "bayburt", "karaman", "kirikkale", "batman", "sirnak", "bartin", "ardahan",
        "igdir", "yalova", "karabuk", "kilis", "osmaniye", "duzce"
    }
YASAKLI_KELIMELER = YASAKLI_KELIMELER | ILCELER 

def get_clean_main_name(full_name):

    

    words = [convert_to_english(w) for w in str(full_name).split()]
    clean_words = [w for w in words if w not in YASAKLI_KELIMELER]

    if not clean_words:
        return "".join(words[:2])

    return "".join(clean_words)


# ---------------- URL ÜRET ----------------
def generate_url_variants(full_name):

    main_name = get_clean_main_name(full_name)
    if not main_name:
        return []

    base_variants = [
        f"{main_name}okullari",
        f"ozel{main_name}okullari",
        f"{main_name}koleji",
        f"{main_name}-okullari",
        f"ozel-{main_name}-okullari",
        f"{main_name}-koleji",
    ]

    uzantilar = [".com", ".com.tr", ".k12.tr"]

    urls = []
    for base in base_variants:
        for ext in uzantilar:
            urls.append(f"http://www.{base}{ext}")

    return urls


# ---------------- DNS KONTROL ----------------
def domain_exists(url):
    try:
        domain = (
            url.replace("http://", "")
               .replace("https://", "")
               .replace("www.", "")
               .split("/")[0]
        )

        socket.gethostbyname(domain)
        return True

    except socket.gaierror:
        return False
    except:
        return False


# ---------------- ANA BULUCU ----------------
def find_active_website(kurum_adi):

    if pd.isna(kurum_adi) or kurum_adi == "":
        return "İsim Yok"

    urls = generate_url_variants(kurum_adi)

    for url in urls:
        if domain_exists(url):
            return url

    return "Bulunamadı"


# ---------------- ANA İŞLEYİCİ ----------------
def ana_isleyici():

    df = pd.read_excel(DOSYA_YOLU)

    if 'Web Sitesi' not in df.columns:
        df['Web Sitesi'] = None

    baslangic = 1500 
    bitis = 2500

    alt_df = df.iloc[baslangic:bitis]

    print(f"{len(alt_df)} kurum DNS üzerinden kontrol ediliyor...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        sonuclar = list(executor.map(find_active_website,
                                     alt_df['Kurum Adı']))

    df.loc[baslangic:bitis-1, 'Web Sitesi'] = sonuclar

    df.to_excel(DOSYA_YOLU, index=False)

    print("✅ İşlem tamamlandı.")


if __name__ == "__main__":
    ana_isleyici()
