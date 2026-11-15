import time
from src.config import load_config
from src.database import get_db_connection
from src.ai.gemini_summarizer import generate_ai_exam_summary
from src.dispatchers import get_dispatcher

cfg = load_config()
disp = get_dispatcher(cfg)

with get_db_connection() as conn:
    c = conn.cursor()
    c.execute("SELECT * FROM articles WHERE source LIKE '%NTA%' AND title LIKE '%JEE%' AND url LIKE '%.pdf' LIMIT 1")
    art = dict(c.fetchone())

insight_msg = generate_ai_exam_summary(art)
print("Insight Msg:\n", insight_msg)

ok1, res1 = disp.send_message(insight_msg)
print("Message Delivered:", ok1, res1)

time.sleep(1.5)
ok2, res2 = disp.send_document(art["url"], caption=f"📄 Official Circular PDF Attached: {art['title'][:70]}")
print("PDF Delivered:", ok2, res2)
