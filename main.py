import sys
import logging
from config import DEPARTMENTS
from scraper import fetch_announcements
from storage import check_for_new_announcements, update_storage
from mailer import send_announcement_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)


def run_tracker(force_test: bool = False) -> None:
    logging.info("KTÜ Duyuru Takipçisi başlatıldı.")

    for dept_key, dept_info in DEPARTMENTS.items():
        dept_url = dept_info.get("url")
        recipients = dept_info.get("recipients", [])

        if not dept_url:
            logging.warning(f"[{dept_key}] URL tanımlanmamış, atlanıyor.")
            continue

        logging.info(f"[{dept_key}] Sayfa kontrol ediliyor: {dept_url}")
        current_announcements = fetch_announcements(dept_url)

        if not current_announcements:
            logging.warning(f"[{dept_key}] Hiçbir duyuru çekilemedi veya sayfa yapısı değişti.")
            continue

        # Yeni duyuru kontrolü
        new_items, is_first_run = check_for_new_announcements(
            department_key=dept_key,
            current_announcements=current_announcements
        )

        # TEST MODU: Yeni duyuru olmasa bile son 2 duyuruyu test için zorla gönder
        if force_test:
            logging.info(f"[{dept_key}] 🧪 TEST MODU AKTİF: Gerçek verilerden son 2 duyuru test maili olarak gönderiliyor...")
            items_to_send = current_announcements[:2]
            send_announcement_email(dept_key, items_to_send, recipients)
            continue

        # Normal Akış: İlk çalıştırma ise sadece hafızaya al
        if is_first_run:
            logging.info(f"[{dept_key}] Sistem ilk kez başlatıldı. Mevcut duyurular kaydedildi, mail gönderilmedi.")
            continue

        # Normal Akış: Yeni duyuru yoksa mail gönderme
        if not new_items:
            logging.info(f"[{dept_key}] Yeni bir duyuru yok. E-posta gönderilmeyecek.")
            update_storage(dept_key, current_announcements)
            continue

        # Normal Akış: Yeni duyuru varsa mail gönder ve storage'ı güncelle
        logging.info(f"[{dept_key}] {len(new_items)} yeni duyuru tespit edildi! E-posta gönderiliyor...")
        success = send_announcement_email(dept_key, new_items, recipients)

        if success:
            update_storage(dept_key, current_announcements)
            logging.info(f"[{dept_key}] İşlem başarıyla tamamlandı.")
        else:
            logging.error(f"[{dept_key}] E-posta gönderilemediği için storage güncellenmedi.")

    logging.info("KTÜ Duyuru Takipçisi çalışmasını tamamladı.")


if __name__ == "__main__":
    is_test = "--test-notify" in sys.argv
    run_tracker(force_test=is_test)