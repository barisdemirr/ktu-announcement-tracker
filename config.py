import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("KTU_BASE_URL", "https://www.ktu.edu.tr").rstrip("/")

SMTP_CONFIG = {
    "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "port": int(os.getenv("SMTP_PORT", 587)),
    "user": os.getenv("SMTP_USER", ""),
    "password": os.getenv("SMTP_PASSWORD", "")
}

# İleride yeni bölüm eklemek istediğinde hem URL'sini hem mail listesini buraya tanımlayabilirsin
DEPARTMENTS = {
    "bilgisayar": {
        "url": os.getenv("DEPT_BILGISAYAR_URL", "https://www.ktu.edu.tr/bilgisayar"),
        "recipients": [
            email.strip() 
            for email in os.getenv("EMAILS_BILGISAYAR", "").split(",") 
            if email.strip()
        ]
    }
    # Örnek: "yazilim": { ... }
}