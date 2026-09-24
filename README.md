# 🎓 KTU Announcement Tracker 📬

> **Never miss a departmental deadline again.** An automated, serverless bot that keeps computer engineering students in the loop with fresh campus announcements delivered straight to their inboxes.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Cost](https://img.shields.io/badge/Hosting_Cost-$0%20(Free)-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

---

## 🎯 Why This Project Exists

Let's be honest: **nobody checks the university website every single day.**

Crucial announcements—like classroom changes, midterm schedules, internship report deadlines, or lab groups—often get published quietly on the department site, and students only notice them when it's already too late.

We built this project with a simple mission: **to make student life easier and ensure none of our classmates miss out on critical updates.** Whenever a new announcement pops up, our bot catches it and delivers a clean notification right to their smartphones.

---

## ✨ Killer Features

- 💸 **$0 Running Cost (Serverless):** No VPS, no cloud bills, no dedicated servers. It runs entirely on **GitHub Actions** and **Gmail SMTP**.
- 🧠 **Smart Deduplication:** If an older announcement is deleted by the department administration, the bot **does not** trigger false alerts. It remembers the last 40 seen links in a lightweight JSON storage.
- 📱 **Clean & Responsive HTML Cards:** No messy raw text. Each announcement arrives as a beautiful card with the date, issuing unit, and a direct button.
- 🔒 **Privacy-First (BCC Delivery):** Classmates can't see each other's email addresses in the `To` field. Everyone's privacy is respected.
- ⏰ **Optimized Cron Schedule:**
  - **Weekdays (Mon–Fri):** 07:38, 12:49, and 17:41 TRT (catches morning, midday, and end-of-day notices).
  - **Weekends (Sat–Sun):** 17:41 TRT.
- 🧩 **Modular & Scalable:** Currently tracking Computer Engineering (`bilgisayar`), but you can add other departments in just 2 lines of config.

---

## 🛠️ How It Works

```text
┌────────────────────────────────┐
│  KTÜ Department Website (SSR)  │
└───────────────┬────────────────┘
                │
                ▼ (Scrape HTML via BeautifulSoup)
┌────────────────────────────────┐
│           scraper.py           │
└───────────────┬────────────────┘
                │
                ▼ (Compare with seen_links)
┌────────────────────────────────┐
│    storage.py (storage.json)   │
└───────────────┬────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
[No New Items]     [New Announcements!]
    │                       │
(Exit silently)             ▼
                ┌────────────────────────┐
                │ mailer.py (Gmail SMTP) │
                └───────────┬────────────┘
                            │
                            ▼
                 📬 Student Inboxes
```

---

## 📁 Project Structure

```text
ktu-announcement-tracker/
├── .github/workflows/
│   └── tracker.yml          # GitHub Actions scheduled runner (Cron)
├── config.py                # Environment and department configurations
├── scraper.py               # BeautifulSoup-powered HTML scraper
├── storage.py               # JSON-based state & deduplication manager
├── mailer.py                # Responsive HTML email builder & SMTP dispatcher
├── main.py                  # Entrypoint orchestration script
├── storage.json             # Persistent announcement cache
├── requirements.txt         # Python dependencies
└── .env.example             # Template for local environment variables
```

---

## 🚀 Getting Started (Local Setup)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ktu-announcement-tracker.git
cd ktu-announcement-tracker
```

### 2. Set up virtual environment & dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure `.env`

Create a `.env` file based on `.env.example`:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_16_digit_app_password

KTU_BASE_URL=https://www.ktu.edu.tr
DEPT_BILGISAYAR_URL=https://www.ktu.edu.tr/bilgisayar
EMAILS_BILGISAYAR=your_email@gmail.com,friend@gmail.com
```

> **Note:** For Gmail, generate a 16-character App Password from your Google Account settings (Security > 2-Step Verification > App Passwords).

### 4. Test it locally

To test the email template with live announcements without waiting for new ones:

```bash
python main.py --test-notify
```

---

## ⚙️ Automated Deployment with GitHub Actions

1. Push this repository to GitHub.
2. Go to **Settings > Secrets and variables > Actions** in your repo.
3. Add the following repository secrets:
   - `SMTP_SERVER`
   - `SMTP_PORT`
   - `SMTP_USER`
   - `SMTP_PASSWORD`
   - `KTU_BASE_URL`
   - `DEPT_BILGISAYAR_URL`
   - `EMAILS_BILGISAYAR`
4. Go to **Settings > Actions > General > Workflow permissions** and select **"Read and write permissions"** so GitHub Actions can commit the updated `storage.json` automatically.

That's it! The bot will now run on schedule and watch the site for you.

---

## 💡 Adding a New Department

Want to track Software Engineering or Electrical Engineering too? Just add them to `.env` and `config.py`:

```python
# config.py
DEPARTMENTS = {
    "bilgisayar": { ... },
    "yazilim": {
        "url": os.getenv("DEPT_YAZILIM_URL"),
        "recipients": [e.strip() for e in os.getenv("EMAILS_YAZILIM", "").split(",") if e.strip()]
    }
}
```

---

## 🤝 Contributing

Got ideas to make this even better (like adding Telegram bot or Discord webhook support)? Pull requests and feedback are always welcome!

---

Crafted with ❤️ for KTU Computer Engineering students.