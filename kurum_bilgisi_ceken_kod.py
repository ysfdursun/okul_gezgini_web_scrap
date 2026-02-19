import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

base_url = "https://ookgm.meb.gov.tr/kurumlar.php"

iller = [
    "ADANA","ADIYAMAN","AFYONKARAHİSAR","AĞRI","AKSARAY","AMASYA","ANKARA","ANTALYA",
    "ARDAHAN","ARTVİN","AYDIN","BALIKESİR","BARTIN","BATMAN","BAYBURT","BİLECİK",
    "BİNGÖL","BİTLİS","BOLU","BURDUR","BURSA","ÇANAKKALE","ÇANKIRI","ÇORUM",
    "DENİZLİ","DİYARBAKIR","DÜZCE","EDİRNE","ELAZIĞ","ERZİNCAN","ERZURUM",
    "ESKİŞEHİR","GAZİANTEP","GİRESUN","GÜMÜŞHANE","HAKKARİ","HATAY","IĞDIR",
    "ISPARTA","İSTANBUL","İZMİR","KAHRAMANMARAŞ","KARABÜK","KARAMAN","KARS",
    "KASTAMONU","KAYSERİ","KIRIKKALE","KIRKLARELİ","KIRŞEHİR","KİLİS",
    "KOCAELİ","KONYA","KÜTAHYA","MALATYA","MANİSA","MARDİN","MERSİN","MUĞLA",
    "MUŞ","NEVŞEHİR","NİĞDE","ORDU","OSMANİYE","RİZE","SAKARYA","SAMSUN",
    "SİİRT","SİNOP","SİVAS","ŞANLIURFA","ŞIRNAK","TEKİRDAĞ","TOKAT","TRABZON",
    "TUNCELİ","UŞAK","VAN","YALOVA","YOZGAT","ZONGULDAK"
]

all_data = []

# Önce ana sayfaya gidip oturumu başlat
driver.get(base_url)
time.sleep(3)
print("Oturum başlatıldı, veri çekme başlıyor...")

def sayfa_bos_mu(driver):
    try:
        table = driver.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        veri_satirlari = [r for r in rows[1:] if r.find_elements(By.TAG_NAME, "td")]
        return len(veri_satirlari) == 0
    except:
        return True  # Tablo bile bulunamadıysa boş say

for il in iller:
    print(f"\n{'='*40}")
    print(f"{il} çekiliyor...")
    sayfa = 1

    while True:
        url = f"{base_url}?sayfa={sayfa}&tur=yurtdisiEgtmDnsmnlk&il={il}&tur2=0"
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
        except:
            pass
        time.sleep(1)

        if sayfa_bos_mu(driver):
            print(f"  → {il} için sayfa {sayfa} boş, sonraki ile geçiliyor.")
            break

        try:
            table = driver.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"  Sayfa {sayfa} - {len(rows)-1} satır bulundu")

            for row in rows[1:]:
                cols = row.find_elements(By.TAG_NAME, "td")
                row_data = [col.text for col in cols]
                if row_data:
                    row_data.append(il)
                    row_data.append(sayfa)
                    all_data.append(row_data)

        except Exception as e:
            print(f"  Hata: {e}, sonraki ile geçiliyor.")
            break

        sayfa += 1

driver.quit()

df = pd.DataFrame(all_data)
df.to_excel("yurt_disi_egitim_danismanligi_kurulusu.xlsx", index=False)
print("\nTüm iller çekildi!")
print(f"Toplam {len(all_data)} kayıt kaydedildi.")