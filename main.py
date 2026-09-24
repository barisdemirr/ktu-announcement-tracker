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


def run_tracker(force_notify_first_run: bool = False) -> None:
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
            current_announcements=current_announcements,
            first_run_notify=force_notify_first_run
        )

        if is_first_run and not force_notify_first_run:
            logging.info(f"[{dept_key}] Sistem ilk kez başlatıldı. Mevcut duyurular kaydedildi, mail gönderilmedi.")
            continue

        if not new_items:
            logging.info(f"[{dept_key}] Yeni bir duyuru yok. E-posta gönderilmeyecek.")
            # Yine de son 3 duyuru yapısını her gün tazelemek için storage'ı güncelle
            update_storage(dept_key, current_announcements)
            continue

        logging.info(f"[{dept_key}] {len(new_items)} yeni duyuru tespit edildi! E-posta gönderiliyor...")
        success = send_announcement_email(dept_key, new_items, recipients)

        if success:
            # Sadece mail başarılı giderse storage'ı güncelle
            update_storage(dept_key, current_announcements)
            logging.info(f"[{dept_key}] İşlem başarıyla tamamlandı.")
        else:
            logging.error(f"[{dept_key}] E-posta gönderilemediği için storage güncellenmedi.")

    logging.info("KTÜ Duyuru Takipçisi çalışmasını tamamladı.")


if __name__ == "__main__":
    # Eğer terminalden "python main.py --test-notify" yazarsan, ilk çalıştırma olsa bile gerçek duyurularla mail atar
    test_mode = "--test-notify" in sys.argv
    run_tracker(force_notify_first_run=test_mode)