import os
import re
from typing import Any, Dict, Optional
import requests
from .pdf_analyzer import extract_pdf_content, extract_deep_notice_summary


def format_executive_insight(article: Dict[str, Any], parsed: Dict[str, Any]) -> str:
    """Format clean, zero-fluff Real Insight in professional English for busy students."""
    exam = article.get("exam_category", "ADMISSION").upper()
    url = article.get("url", "")
    source = article.get("source", "Official Notice")

    lines = [
        f"🎓 *[{exam} • OFFICIAL CIRCULAR INSIGHT]* 🚨",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📌 *Topic*: {parsed.get('subject', article.get('title'))}"
    ]

    if parsed.get("notice_date"):
        lines.append(f"📅 *Official Date*: {parsed['notice_date']}")

    # Key Insights & Decisions
    points = parsed.get("core_points", [])
    if points:
        lines.append("\n⚡ *KEY INSIGHTS & DECISIONS*:")
        for pt in points[:3]:
            # Clean up into readable bullet
            clean_pt = re.sub(r"^(valid application|fresh application|last date|fee|one attempt per session):\s*", "", pt, flags=re.IGNORECASE)
            lines.append(f"• {clean_pt}")

    # Deadlines & Important Dates
    dates = parsed.get("key_dates", [])
    if dates:
        lines.append("\n⏰ *CRITICAL DEADLINES & DATES*:")
        for d in dates[:3]:
            lines.append(f"• {d}")

    # Important Advisory / Candidate Rules
    if len(points) > 3:
        clean_warning = re.sub(r"^(one attempt per session|fee|warning):\s*", "", points[3], flags=re.IGNORECASE)
        lines.append(f"\n⚠️ *IMPORTANT ADVISORY & RULES*:\n• {clean_warning}")

    if parsed.get("helpline"):
        lines.append(f"\n📞 *Official Helpline*: {parsed['helpline']}")

    lines.extend([
        "",
        f"🔗 *Direct Official Link*:\n{url}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "🤖 _Mera Exam Bot • 30-Min Realtime Insight Scanner_"
    ])

    return "\n".join(lines)


def generate_ai_exam_summary(article: Dict[str, Any], api_key: Optional[str] = None) -> str:
    """
    Generate deep, comprehensive exam notice analysis.
    Reads PDF/article content thoroughly and extracts the exact executive insight in English.
    """
    title = article.get("title", "")
    url = article.get("url", "")
    exam = article.get("exam_category", "EXAM").upper()
    source = article.get("source", "Official Notification")
    pub_date = article.get("published_date", "")

    # 1. Download and extract full PDF content if URL points to a PDF
    pdf_text = None
    if url.lower().endswith(".pdf") or "/download/notice/" in url.lower():
        pdf_text = extract_pdf_content(url)

    # 2. Extract deep structured insights
    if pdf_text:
        parsed = extract_deep_notice_summary(pdf_text, title)
        return format_executive_insight(article, parsed)

    # 3. For Web Articles / Non-PDF updates
    clean_title = re.sub(r"^\[.*?\]\s*", "", title)
    
    return (
        f"🎓 *[{exam} • OFFICIAL UPDATE & INSIGHT]* 📢\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Topic*: {clean_title}\n"
        f"🏛️ *Source*: {source}\n"
        f"📅 *Date*: {pub_date}\n\n"
        f"⚡ *KEY INSIGHTS*:\n"
        f"• Official notification released for {exam} candidates.\n"
        f"• Check the direct official link below for full application schedule and candidate instructions.\n\n"
        f"🔗 *Direct Official Link*:\n{url}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 _Mera Exam Bot • 30-Min Realtime Insight Scanner_"
    )
