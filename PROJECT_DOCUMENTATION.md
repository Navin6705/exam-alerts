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
