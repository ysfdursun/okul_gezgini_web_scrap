import pandas as pd
import socket
import requests
import re
from concurrent.futures import ThreadPoolExecutor

# ---------------- AYARLAR ----------------
DOSYA_YOLU = "KurumlarınTamListesi.xlsx"
MAX_WORKERS = 15

GOOGLE_API_KEY = "AIzaSyB4g-JRd4kWuPtPo0lzlZifTteVe2MnLjQ"
SEARCH_ENGINE_ID = "1663c275fb63a4a6c"

# ---------------- TEXT TEMİZLEME ----------------
def convert_to_english(text):
    if not isinstance(text, str):
        return ""
    translations = str.maketrans("çğışıöüÇĞİŞÖÜ", "cgisiouCGISOU")
    return text.lower().translate(translations)

def normalize_word(text):
    text = convert_to_english(text)
    return re.sub(r"[^a-z0-9]", "", text)

# ---------------- İLÇELER ----------------
def load_ilceler_from_csv(path):
    df = pd.read_csv(path)
    return set(normalize_word(x) for x in df["ilce_yeni"].dropna())

ILCELER = load_ilceler_from_csv("temiz_ingilizce_ilceler.csv")

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

# ---------------- İSİM TEMİZLE ----------------
def get_clean_main_name(full_name):

    words = [normalize_word(w) for w in str(full_name).split()]
    clean_words = [w for w in words if w not in YASAKLI_KELIMELER]

    if not clean_words:
        return "".join(words[:2])

    return "".join(clean_words)

# ---------------- URL ÜRET ----------------
def generate_url_variants(full_name):

    main = get_clean_main_name(full_name)

    if not main:
        return []

    bases = [
        f"{main}okullari",
        f"ozel{main}",
        f"{main}koleji",
        f"{main}-okullari",
        f"{main}-koleji"
    ]

    exts = [".com", ".com.tr", ".k12.tr"]

    return [f"http://www.{b}{e}" for b in bases for e in exts]

# ---------------- DNS KONTROL ----------------
def domain_exists(url):
    try:
        domain = (
            url.replace("http://","")
               .replace("https://","")
               .replace("www.","")
               .split("/")[0]
        )
        socket.gethostbyname(domain)
        return True
    except:
        return False

# ---------------- GOOGLE SEARCH ----------------
def google_search_website(query):

    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": 5
    }

    try:
        r = requests.get(url, params=params, timeout=6)
        data = r.json()

        if "items" in data:
            for item in data["items"]:
                link = item["link"]

                # gereksiz siteleri ele
                if any(x in link for x in [
                    "facebook","instagram","linkedin",
                    "youtube","meb.gov","google.com/maps"
                ]):
                    continue

                return link

    except Exception as e:
        print("Google API hata:", e)

    return None

# ---------------- ANA BULUCU ----------------
def find_active_website(kurum_adi, ilce):

    if pd.isna(kurum_adi):
        return "İsim Yok"

    # 1️⃣ DNS yöntemi
    urls = generate_url_variants(kurum_adi)

    for url in urls:
        if domain_exists(url):
            return url

    # 2️⃣ GOOGLE SEARCH
    query = f"{kurum_adi} {ilce} resmi sitesi"

    sonuc = google_search_website(query)

    if sonuc:
        return sonuc

    return "Bulunamadı"

# ---------------- ANA İŞLEYİCİ ----------------
def ana_isleyici():

    df = pd.read_excel(DOSYA_YOLU)

    if "Web Sitesi" not in df.columns:
        df["Web Sitesi"] = None

    baslangic = 3010
    bitis = 3015

    alt_df = df.iloc[baslangic:bitis]

    print(f"{len(alt_df)} kurum kontrol ediliyor...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        sonuclar = list(
            executor.map(
                lambda x: find_active_website(x[0], x[1]),
                zip(alt_df["Kurum Adı"], alt_df["İlçe"])
            )
        )

    df.loc[baslangic:bitis-1, "Web Sitesi"] = sonuclar

    df.to_excel(DOSYA_YOLU, index=False)

    print("✅ TAMAMLANDI")

# ---------------- ÇALIŞTIR ----------------
if __name__ == "__main__":
    ana_isleyici()
