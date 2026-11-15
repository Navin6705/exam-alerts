from src.config import load_config
from src.database import get_db_connection
from src.ai.gemini_summarizer import generate_ai_exam_summary
from src.dispatchers import get_dispatcher

cfg = load_config()
disp = get_dispatcher(cfg)

with get_db_connection() as conn:
    c = conn.cursor()
    c.execute("SELECT * FROM articles WHERE source LIKE '%NTA%' AND title LIKE '%JEE%' LIMIT 1")
    row = c.fetchone()
    art = dict(row)

print("Title:", art["title"])
print("Calling Gemini AI...")
ai_msg = generate_ai_exam_summary(art, cfg["gemini"]["api_key"])
print("AI Summary:\n", ai_msg)

print("\nDispatching to Telegram...")
ok, res = disp.send_message(ai_msg)
print("Telegram Status:", ok, res)
