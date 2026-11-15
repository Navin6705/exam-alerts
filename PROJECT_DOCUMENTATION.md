# EduAlert • Automated Exam & Admissions Intelligence Bot
**Master Technical Documentation & Living Architecture Guide**

---

## 1. Executive Summary & Philosophy: "Zero-Fluff Real Insights"
Students and parents do not have time to read 10-page bureaucratic circulars or search through lengthy PDFs. The core philosophy of **EduAlert** is **"Real Actionable Insights in 15 Seconds"**:

1. **Background Deep Ingestion**: The system continuously reads raw circulars and extracts the exact operational decisions.
2. **Professional English Real Insight Telegram Delivery**:
   - 📌 **Topic & Official Date**
   - ⚡ **KEY INSIGHTS & DECISIONS**: Direct decisions, changes, rules.
   - ⏰ **CRITICAL DEADLINES & DATES**: Exact last dates and cutoff timings (e.g., 11:50 PM).
   - ⚠️ **IMPORTANT ADVISORY & RULES**: Crucial warnings (refund policy, duplicate attempts, verification).
   - 📞 **Official Helpline**: Official numbers and email.
   - 🔗 **Direct Official Link**: Direct application/notice URL.
   - 📄 **Official PDF Document**: Delivered as an attached file directly in chat.
3. **Automated 30-Minute Autopilot**: Runs every 30 minutes in background, scans all 19 portals, analyzes new notices, and alerts immediately.

---

## 2. Real-Time Tracking Stats (Live Database)
- **Total Tracked Notices in Database**: **1,085+ live records**
- **Interval**: Every 30 minutes (`polling_interval_minutes: 30`)
- **Deduplication Method**: SHA-256 fingerprinting on `(title + clean_url)`
- **Delivery Destination**: Telegram Chat ID `908431939` (`@Mera_exams_bot`)

---

## 3. Chronological Changelog
- **v2.0.0 (2026-11-15)**:
  - **Full 24/7 Cloud Autopilot Verified**: GitHub Actions cloud runner (#2) successfully ran all 19 scrapers in 1m 6s.
  - Successfully communicated with Telegram Bot API and committed updated SQLite database state back to GitHub (`EduAlert-Bot`).
  - Zero-maintenance, serverless architecture fully operational on 30-minute cron schedule.
- **v1.9.0 (2026-11-15)**:
  - Added `pymupdf`, `python-dotenv`, and `urllib3` to `requirements.txt` to eliminate cloud runner `ModuleNotFoundError`.
  - Added resilient fallback import for `pymupdf` in `src/ai/pdf_analyzer.py` guaranteeing zero-crash operation on any OS.
- **v1.8.0 (2026-11-15)**:
  - Upgraded Google News web article summarizer to generate full structured Real Insights (Key Insights & Decisions, Critical Deadlines, Advisories) matching official circular quality.
  - Successfully scraped and dispatched real-time Google News test bulletins for JEE Main, NEET UG, and JEE Advanced to Telegram with Status 200.
- **v1.7.0 (2026-11-15)**:
  - Upgraded Telegram message rendering engine from legacy Markdown to native HTML (`<b>`, `<i>`, `html.escape()`) ensuring 100% robust bold formatting across all mobile and desktop Telegram apps.
  - Hardened GitHub Actions automated 30-minute cloud runner (`exam_monitor.yml`) to use GitHub Repository Secrets (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) with explicit fallback to Telegram dispatcher.
- **v1.6.0 (2026-11-15)**:
  - Converted all bulletin section headers into clean, professional English (`KEY INSIGHTS & DECISIONS`, `CRITICAL DEADLINES & DATES`, `IMPORTANT ADVISORY & RULES`).
  - Tested and delivered live sample bulletin to Telegram.
- **v1.5.0 (2026-11-15)**:
  - Redesigned message format to pure **Real Insights & Executive Summaries**.
  - Configured automated 30-minute background scanning cycle across all Gujarat and national portals.
- **v1.4.0 (2026-11-15)**:
  - Expanded coverage to 19 portals: ACPC Gujarat, Nirma, DA-IICT, PDPU, Adani, GUJCET, GSEB, NTA Twitter, JEE Adv, MHT CET, COMEDK, MET, WBJEE.
- **v1.3.0 (2026-11-15)**:
  - Implemented Telegram automatic PDF document attachment (`sendDocument`).
- **v1.2.0 (2026-11-15)**:
  - Added Linux server deployment script, systemd unit, and Dockerfile.
- **v1.0.0 (2026-11-15)**:
  - Initial system architecture designed and deployed.
