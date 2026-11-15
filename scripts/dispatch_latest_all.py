import time
from typing import Dict, Any, List
from src.config import load_config
from src.database import get_db_connection
from src.dispatchers import get_dispatcher
from src.formatters.message_formatter import get_exam_emoji

CATEGORIES_ORDER = [
    # Gujarat B.Tech & Boards
    ("ACPC", "🦁 ACPC Gujarat (BE/B.Tech)"),
    ("NIRMA", "🏛️ Nirma University B.Tech"),
    ("DAIICT", "💻 DA-IICT Admissions"),
    ("PDPU", "🛢️ PDPU / PDEU Admissions"),
    ("ADANI", "🏙️ Adani University B.Tech"),
    ("GUJCET", "⚡ GUJCET (GSEB)"),
    ("GSEB", "📚 GSEB 12th Science Board"),
    
    # National Central Entrances
    ("NTA", "🇮🇳 NTA Official Notices"),
    ("NTA_TWITTER", "🐦 NTA Twitter / Breaking"),
    ("JEE", "📐 JEE Main (Session 1 & 2)"),
    ("JEE_ADV", "🏆 JEE Advanced (IIT)"),
    ("NEET", "🩺 NEET UG & PG"),
    ("CUET", "🎓 CUET UG / PG"),
    
    # State CETs & Top Private Entrances
    ("VITEEE", "🏛️ VITEEE (VIT Vellore)"),
    ("MHT_CET", "🚩 MHT CET (Maharashtra)"),
    ("COMEDK", "🎯 COMEDK UGET (Karnataka)"),
    ("MET", "🏥 MET (Manipal Entrance)"),
    ("WBJEE", "🏛️ WBJEE (West Bengal)")
]


def send_all_latest_notifications():
    cfg = load_config()
    disp = get_dispatcher(cfg)
    
    print("Collecting latest notices for all institutions...")
    latest_items: List[Dict[str, Any]] = []

    with get_db_connection() as conn:
        for cat_code, display_name in CATEGORIES_ORDER:
            # Pick the best non-mailto notice
            row = conn.execute("""
                SELECT * FROM articles 
                WHERE exam_category = ? AND url NOT LIKE '%mailto:%' AND url NOT LIKE '%tel:%'
                ORDER BY id DESC LIMIT 1
            """, (cat_code,)).fetchone()

            if row:
                art = dict(row)
                art["display_name"] = display_name
                latest_items.append(art)
            else:
                # Fallback to general search if category was sparse
                row_gen = conn.execute("""
                    SELECT * FROM articles 
                    WHERE (title LIKE ? OR source LIKE ?) AND url NOT LIKE '%mailto:%'
                    ORDER BY id DESC LIMIT 1
                """, (f"%{cat_code}%", f"%{cat_code}%")).fetchone()
                if row_gen:
                    art = dict(row_gen)
                    art["display_name"] = display_name
                    latest_items.append(art)

    print(f"Found {len(latest_items)} latest category updates.")

    # 1. Master Mega Bulletin Message (Gujarat Core)
    lines_gujarat = [
        "🦁 *LATEST GUJARAT ADMISSIONS UPDATES*",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    lines_national = [
        "🇮🇳 *LATEST NATIONAL & STATE ENTRANCE EXAMS*",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]

    gujarat_codes = {"ACPC", "NIRMA", "DAIICT", "PDPU", "ADANI", "GUJCET", "GSEB"}

    for art in latest_items:
        cat = art["exam_category"]
        disp_name = art["display_name"]
        title = art["title"]
        url = art["url"]

        block = f"*{disp_name}*\n📌 {title}\n🔗 {url}\n"

        if cat in gujarat_codes:
            lines_gujarat.append(block)
        else:
            lines_national.append(block)

    lines_gujarat.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🤖 _Mera Exam Bot • Gujarat Admissions_")
    lines_national.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🤖 _Mera Exam Bot • National Entrances_")

    msg_gujarat = "\n".join(lines_gujarat)
    msg_national = "\n".join(lines_national)

    print("\nSending Gujarat Admissions Bulletin...")
    ok1, res1 = disp.send_message(msg_gujarat)
    print("Gujarat Bulletin Status:", ok1, res1)
    time.sleep(2.0)

    print("\nSending National Entrance Bulletin...")
    ok2, res2 = disp.send_message(msg_national)
    print("National Bulletin Status:", ok2, res2)
    time.sleep(2.0)

    # 2. Also send ACPC and NTA official PDF circular documents
    with get_db_connection() as conn:
        pdf_rows = conn.execute("""
            SELECT * FROM articles 
            WHERE url LIKE '%.pdf' AND (exam_category IN ('ACPC', 'NTA', 'JEE', 'PDPU', 'ADANI'))
            ORDER BY id DESC LIMIT 2
        """).fetchall()

        for r in pdf_rows:
            p_art = dict(r)
            caption = f"📄 *{p_art['exam_category']} Official Circular Attached*\n{p_art['title'][:80]}"
            print(f"Sending attached PDF: {p_art['url']}...")
            disp.send_document(p_art['url'], caption=caption)
            time.sleep(2.0)

    print("\n✅ All latest notifications and circulars dispatched to Telegram successfully!")


if __name__ == "__main__":
    send_all_latest_notifications()
