import html
import os
import re
from typing import Any, Dict, Optional
import requests
from .pdf_analyzer import extract_pdf_content, extract_deep_notice_summary


def format_executive_insight(article: Dict[str, Any], parsed: Dict[str, Any]) -> str:
    """Format clean, zero-fluff Real Insight in professional HTML bolding for Telegram."""
    exam = html.escape(article.get("exam_category", "ADMISSION").upper())
    url = article.get("url", "")
    source = html.escape(article.get("source", "Official Notice"))
    subject = html.escape(parsed.get('subject', article.get('title', '')))

    lines = [
        f"🎓 <b>[{exam} • OFFICIAL CIRCULAR INSIGHT]</b> 🚨",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📌 <b>Topic</b>: {subject}"
    ]

    if parsed.get("notice_date"):
        lines.append(f"📅 <b>Official Date</b>: {html.escape(parsed['notice_date'])}")

    # Key Insights & Decisions
    points = parsed.get("core_points", [])
    if points:
        lines.append("\n⚡ <b>KEY INSIGHTS & DECISIONS</b>:")
        for pt in points[:3]:
            clean_pt = re.sub(r"^(valid application|fresh application|last date|fee|one attempt per session):\s*", "", pt, flags=re.IGNORECASE)
            lines.append(f"• {html.escape(clean_pt)}")

    # Deadlines & Important Dates
    dates = parsed.get("key_dates", [])
    if dates:
        lines.append("\n⏰ <b>CRITICAL DEADLINES & DATES</b>:")
        for d in dates[:3]:
            lines.append(f"• {html.escape(d)}")

    # Important Advisory / Candidate Rules
    if len(points) > 3:
        clean_warning = re.sub(r"^(one attempt per session|fee|warning):\s*", "", points[3], flags=re.IGNORECASE)
        lines.append(f"\n⚠️ <b>IMPORTANT ADVISORY & RULES</b>:\n• {html.escape(clean_warning)}")

    if parsed.get("helpline"):
        lines.append(f"\n📞 <b>Official Helpline</b>: {html.escape(parsed['helpline'])}")

    lines.extend([
        "",
        f"🔗 <b>Direct Official Link</b>:\n{url}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "🤖 <i>Mera Exam Bot • 30-Min Realtime Insight Scanner</i>"
    ])

    return "\n".join(lines)


def generate_ai_exam_summary(article: Dict[str, Any], api_key: Optional[str] = None) -> str:
    """
    Generate deep, comprehensive exam notice analysis.
    Reads PDF/article content thoroughly and extracts the exact executive insight in HTML.
    """
    title = article.get("title", "")
    url = article.get("url", "")
    exam = html.escape(article.get("exam_category", "EXAM").upper())
    source = html.escape(article.get("source", "Official Notification"))
    pub_date = html.escape(article.get("published_date", ""))

    # 1. Download and extract full PDF content if URL points to a PDF
    pdf_text = None
    if url.lower().endswith(".pdf") or "/download/notice/" in url.lower():
        pdf_text = extract_pdf_content(url)

    # 2. Extract deep structured insights
    if pdf_text:
        parsed = extract_deep_notice_summary(pdf_text, title)
        return format_executive_insight(article, parsed)

    # 3. For Web Articles / Non-PDF updates
    clean_title = html.escape(re.sub(r"^\[.*?\]\s*", "", title))
    
    return (
        f"🎓 <b>[{exam} • OFFICIAL UPDATE & INSIGHT]</b> 📢\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Topic</b>: {clean_title}\n"
        f"🏛️ <b>Source</b>: {source}\n"
        f"📅 <b>Date</b>: {pub_date}\n\n"
        f"⚡ <b>KEY INSIGHTS</b>:\n"
        f"• Official notification released for {exam} candidates.\n"
        f"• Check the direct official link below for full application schedule and candidate instructions.\n\n"
        f"🔗 <b>Direct Official Link</b>:\n{url}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <i>Mera Exam Bot • 30-Min Realtime Insight Scanner</i>"
    )
