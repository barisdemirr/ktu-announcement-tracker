import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict

from config import SMTP_CONFIG

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def build_email_content(department_name: str, announcements: List[Dict[str, str]]) -> tuple[str, str]:
    """
    Duyuruları düz metin (plain text) ve şık kartlardan oluşan HTML şablonuna dönüştürür.
    """
    total = len(announcements)
    dept_title = department_name.replace("_", " ").title()

    # --- DÜZ METİN VERSİYONU (Fallback) ---
    plain_lines = [
        f"KTÜ {dept_title} Bölümü - Yeni Duyuru Bildirimi",
        f"Toplam {total} yeni duyuru tespit edildi.\n",
        "-" * 50
    ]
    for idx, item in enumerate(announcements, start=1):
        plain_lines.append(f"{idx}. {item['title']}")
        plain_lines.append(f"   Tarih: {item['date']} | Birim: {item.get('unit', '-')}")
        plain_lines.append(f"   Link : {item['link']}\n")
    plain_text = "\n".join(plain_lines)

    # --- HTML SECTIONS (KARTLAR) ---
    cards_html = ""
    for item in announcements:
        card = f"""
        <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="margin-bottom: 8px;">
                <span style="display: inline-block; background-color: #e0f2fe; color: #0369a1; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 4px; margin-right: 8px;">
                    📅 {item['date']}
                </span>
                <span style="display: inline-block; background-color: #f1f5f9; color: #475569; font-size: 12px; padding: 4px 10px; border-radius: 4px;">
                    🏛️ {item.get('unit', 'Bölüm')}
                </span>
            </div>
            <h3 style="margin: 0 0 12px 0; font-size: 16px; color: #0f172a; line-height: 1.4; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                {item['title']}
            </h3>
            <div style="margin-top: 12px;">
                <a href="{item['link']}" target="_blank" style="display: inline-block; background-color: #00426a; color: #ffffff; text-decoration: none; font-size: 13px; font-weight: 600; padding: 8px 16px; border-radius: 6px;">
                    Duyuruya Git &rarr;
                </a>
            </div>
        </div>
        """
        cards_html += card

    # --- TAM HTML ŞABLONU ---
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; padding: 30px 10px;">
            <tr>
                <td align="center">
                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 620px; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0;">
                        <!-- HEADER -->
                        <tr>
                            <td style="background-color: #00426a; padding: 24px 28px; text-align: left;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 20px; font-weight: 700; letter-spacing: -0.3px;">
                                    KTÜ {dept_title}
                                </h1>
                                <p style="margin: 6px 0 0 0; color: #93c5fd; font-size: 13px;">
                                    Yeni Duyuru Bildirimi ({total} Yeni İçerik)
                                </p>
                            </td>
                        </tr>
                        <!-- BODY CONTENT -->
                        <tr>
                            <td style="padding: 24px 28px; background-color: #f8fafc;">
                                {cards_html}
                            </td>
                        </tr>
                        <!-- FOOTER -->
                        <tr>
                            <td style="padding: 16px 28px; background-color: #f1f5f9; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="margin: 0; font-size: 12px; color: #64748b;">
                                    Bu e-posta otomatik bildirim sistemi tarafından gönderilmiştir.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    return plain_text, html_content


def send_announcement_email(
    department_name: str, 
    announcements: List[Dict[str, str]], 
    recipients: List[str]
) -> bool:
    """
    Yeni duyuruları ilgili alıcılara SMTP üzerinden gönderir.
    """
    if not announcements:
        logging.info("Gönderilecek duyuru bulunamadı.")
        return False

    if not recipients:
        logging.warning(f"[{department_name}] Alıcı mail listesi boş, mail atılmadı.")
        return False

    server_host = SMTP_CONFIG["server"]
    server_port = SMTP_CONFIG["port"]
    user = SMTP_CONFIG["user"]
    password = SMTP_CONFIG["password"]

    if not user or not password:
        logging.error("SMTP_USER veya SMTP_PASSWORD tanımlı değil! .env dosyasını kontrol et.")
        return False

    subject = f"KTÜ {department_name.title()} - {len(announcements)} Yeni Duyuru"
    plain_text, html_body = build_email_content(department_name, announcements)

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"KTÜ Duyuru Takipçisi <{user}>"
    message["To"] = ", ".join(recipients)

    message.attach(MIMEText(plain_text, "plain", "utf-8"))
    message.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        logging.info(f"SMTP bağlantısı kuruluyor ({server_host}:{server_port})...")
        with smtplib.SMTP(server_host, server_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, password)
            server.sendmail(user, recipients, message.as_string())

        logging.info(f"Mail başarıyla gönderildi: {recipients}")
        return True
    except Exception as e:
        logging.error(f"E-posta gönderilirken hata oluştu: {e}")
        return False


if __name__ == "__main__":
    # Test çalıştırması: Sahte bir duyuru ile mail fonksiyonunu test edelim
    from config import DEPARTMENTS

    recipients_list = DEPARTMENTS["bilgisayar"]["recipients"]
    print(f"Hedef alıcılar: {recipients_list}")

    mock_announcements = [
        {
            "title": "Test Duyurusu: 2026-2027 Güz Yarıyılı Bilgilendirmesi",
            "date": "24 Eylül",
            "unit": "Bilgisayar Mühendisliği",
            "link": "https://www.ktu.edu.tr/bilgisayar"
        },
        {
            "title": "İkinci Test: Laboratuvar Grupları Hakkında",
            "date": "23 Eylül",
            "unit": "Bölüm Başkanlığı",
            "link": "https://www.ktu.edu.tr/bilgisayar"
        }
    ]

    # .env içinde SMTP_USER ve SMTP_PASSWORD doğruysa test maili gönderecektir
    send_announcement_email("bilgisayar", mock_announcements, recipients_list)