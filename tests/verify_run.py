from src.database import get_stats, get_recent_articles

stats = get_stats()
print("TOTAL ARTICLES:", stats["total_articles"])
print("SENT ALERTS:", stats["sent_alerts"])
print("PENDING ALERTS:", stats["pending_alerts"])
print("EXAM COUNTS:", stats["exam_counts"])
print("--- SAMPLES ---")
for a in get_recent_articles(limit=8):
    print(f"[{a['exam_category']}] [{a['priority']}] {a['title'][:70]}... -> {a['delivery_status']}")
