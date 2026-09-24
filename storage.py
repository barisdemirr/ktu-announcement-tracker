import json
import os
import logging
from typing import List, Dict, Tuple

STORAGE_FILE = "storage.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_storage() -> Dict:
    """JSON dosyasından kayıtlı duyuru geçmişini okur."""
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Storage dosyası okunurken hata: {e}")
        return {}


def save_storage(data: Dict) -> None:
    """Duyuru geçmişini JSON dosyasına kaydeder."""
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Storage dosyasına yazılırken hata: {e}")


def check_for_new_announcements(
    department_key: str, 
    current_announcements: List[Dict[str, str]], 
    first_run_notify: bool = False
) -> Tuple[List[Dict[str, str]], bool]:
    """
    Mevcut duyuruları kayıtlı olanlarla karşılaştırır.
    
    Dönüş:
        (new_announcements, is_first_run)
    """
    storage = load_storage()
    dept_data = storage.get(department_key)

    # 1. Senaryo: Bu bölüm için ilk kez çalışıyorsa
    if dept_data is None:
        logging.info(f"[{department_key}] İlk kez çalıştırılıyor. Mevcut durum baz alınıyor...")
        update_storage(department_key, current_announcements)
        if first_run_notify:
            return current_announcements, True
        return [], True

    seen_links = set(dept_data.get("seen_links", []))
    new_announcements = []

    # 2. Senaryo: Sitedeki duyuruları tara, daha önce görülmemiş olanları listele
    for item in current_announcements:
        if item["link"] not in seen_links:
            new_announcements.append(item)

    return new_announcements, False


def update_storage(department_key: str, current_announcements: List[Dict[str, str]]) -> None:
    """
    Bölümün son 3 duyurusunu ve görülen son duyuru linklerini JSON dosyasına yazar.
    """
    storage = load_storage()
    dept_data = storage.get(department_key, {"seen_links": []})

    existing_seen = dept_data.get("seen_links", [])
    
    # Mevcut çekilen duyuru linklerini ekle
    current_links = [item["link"] for item in current_announcements]
    
    # Sırayı koruyarak tekilleştir (en yeni olanlar başta kalacak şekilde)
    combined_links = []
    for link in current_links + existing_seen:
        if link not in combined_links:
            combined_links.append(link)

    # Dosyanın sonsuza kadar büyümemesi için son 40 linki sakla
    updated_seen = combined_links[:40]

    # İstediğin gibi her günün en güncel son 3 duyurusunu tam detaylı tut
    last_top_3 = current_announcements[:3]

    storage[department_key] = {
        "last_top_announcements": last_top_3,
        "seen_links": updated_seen
    }

    save_storage(storage)
    logging.info(f"[{department_key}] Storage güncellendi. Son 3 duyuru ve {len(updated_seen)} link kaydedildi.")


if __name__ == "__main__":
    # Test çalıştırması:
    from scraper import fetch_announcements
    from config import DEPARTMENTS

    dept_url = DEPARTMENTS["bilgisayar"]["url"]
    live_data = fetch_announcements(dept_url)

    new_items, is_first = check_for_new_announcements("bilgisayar", live_data)
    print(f"\nİlk çalıştırma mı? {is_first}")
    print(f"Yeni duyuru sayısı: {len(new_items)}")

    # Storage'a kaydet
    update_storage("bilgisayar", live_data)

    # İkinci kez kontrol ettiğimizde 0 yeni duyuru vermeli (test doğrulaması)
    second_check, _ = check_for_new_announcements("bilgisayar", live_data)
    print(f"İkinci kontrol (0 beklenir): {len(second_check)} yeni duyuru.")