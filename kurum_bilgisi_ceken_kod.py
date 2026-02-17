import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote

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

# Filtrelenecek kurum türü
tur2_text = "Özel Türk Okul Öncesi Kurumu"
tur2_encoded = quote(tur2_text)

all_data = []

for il in iller:
    print(f"{il} çekiliyor...")

    url = f"{base_url}?tur=okul&il={il}&tur2={tur2_encoded}"
    driver.get(url)

    time.sleep(3)

    table = driver.find_element(By.TAG_NAME, "table")
    rows = table.find_elements(By.TAG_NAME, "tr")

    print("Satır sayısı:", len(rows))

    for row in rows[1:]:
        cols = row.find_elements(By.TAG_NAME, "td")
        row_data = [col.text for col in cols]

        if row_data:
            row_data.append(il)
            all_data.append(row_data)

driver.quit()

# DataFrame kolon başlıkları (siteye göre düzenleyebilirsin)
df = pd.DataFrame(all_data)
df.to_excel("ozel_turk_okul_oncesi_kurumlari.xlsx", index=False)

print("Tüm iller çekildi ")
