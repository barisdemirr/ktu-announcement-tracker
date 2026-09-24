from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from config import BASE_URL

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_announcements(department_url: str) -> list[dict]:
    """
    Belirtilen bölüm URL'sinden duyuruları çeker ve yapılandırılmış
    bir liste olarak döner.
    """
    try:
        response = requests.get(department_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"[-] Sayfa yüklenirken hata oluştu ({department_url}): {error}")
        return []

    # KTÜ sayfaları utf-8 kodlamasında
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    announcements_container = soup.find("div", id="carousel-duyuru")
    if not announcements_container:
        print("[-] Duyuru container'ı ('carousel-duyuru') sayfada bulunamadı.")
        return []

    announcement_cards = announcements_container.find_all("a", class_="d1")
    announcements = []

    for card in announcement_cards:
        # 1. Link kontrolü
        raw_href = card.get("href", "").strip()
        if not raw_href:
            continue
        full_link = urljoin(BASE_URL + "/", raw_href)

        # 2. Tarih ayrıştırma (Örn: '24' ve 'Eylül')
        day_tag = card.find("h3", class_="dh3")
        month_tag = card.find("p", class_="dp1")
        day = day_tag.get_text(strip=True) if day_tag else ""
        month = month_tag.get_text(strip=True) if month_tag else ""
        date_str = f"{day} {month}".strip()

        # 3. Başlık
        title_tag = card.find("div", class_="dp2")
        title = title_tag.get_text(strip=True) if title_tag else "Başlıksız Duyuru"

        # 4. İlgili birim / alt başlık (Örn: 'Bilgisayar Mühendisliği')
        dept_tag = card.find("p", class_="dp3")
        dept_name = dept_tag.get_text(strip=True) if dept_tag else ""

        # Benzersiz kimlik olarak duyurunun URL slug'ını veya tam linkini alıyoruz
        announcements.append({
            "id": full_link,
            "title": title,
            "date": date_str,
            "link": full_link,
            "department": dept_name
        })

    return announcements


if __name__ == "__main__":
    # Test amaçlı doğrudan çalıştırıldığında çıktıyı görelim:
    test_url = "https://www.ktu.edu.tr/bilgisayar"
    print(f"[*] Duyurular çekiliyor: {test_url}")
    results = fetch_announcements(test_url)
    print(f"[+] Toplam {len(results)} duyuru bulundu:\n")

    for index, item in enumerate(results[:5], start=1):
        print(f"{index}. [{item['date']}] {item['title']}")
        print(f"   Link: {item['link']}")
        print(f"   Birim: {item['department']}\n")