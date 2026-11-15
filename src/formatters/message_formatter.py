import html
from typing import Any, Dict, List


def get_exam_emoji(category: str) -> str:
    """Return appropriate emoji for exam category."""
    cat = category.upper()
    if "JEE_ADV" in cat:
        return "🏆"
    elif "JEE" in cat:
        return "📐"
    elif "NEET" in cat:
        return "🩺"
    elif "ACPC" in cat:
        return "🦁"
    elif "GUJCET" in cat:
        return "⚡"
    elif "GSEB" in cat:
        return "📚"
    elif "NIRMA" in cat:
        return "🏛️"
    elif "DAIICT" in cat:
        return "💻"
    elif "PDPU" in cat:
        return "🛢️"
    elif "ADANI" in cat:
        return "🏙️"
    elif "MHT" in cat:
        return "🚩"
    elif "COMEDK" in cat:
        return "🎯"
    elif "MET" in cat:
        return "🏥"
    elif "WBJEE" in cat:
        return "🏛️"
    elif "GSAUCA" in cat:
        return "🌾"
    elif "TWITTER" in cat:
        return "🐦"
    elif "VIT" in cat:
        return "🏛️"
    elif "NTA" in cat:
        return "🇮🇳"
    elif "CUET" in cat:
        return "🎓"
    return "📚"


def get_priority_badge(priority: str) -> str:
    """Return badge based on priority."""
    p = priority.upper()
    if p == "HIGH":
        return "🚨 <b>URGENT ALERT</b>"
    elif p == "MEDIUM":
        return "📢 <b>IMPORTANT UPDATE</b>"
    return "ℹ️ <b>ADMISSION NEWS</b>"


def format_single_article_message(article: Dict[str, Any]) -> str:
    """
    Format a single article into a clean, rich message in HTML format.
    """
    category = html.escape(article.get("exam_category", "EXAM").upper())
    emoji = get_exam_emoji(category)
    badge = get_priority_badge(article.get("priority", "MEDIUM"))
    title = html.escape(article.get("title", "No Title"))
    source = html.escape(article.get("source", "Official Notification"))
    url = article.get("url", "")
    pub_date = html.escape(article.get("published_date", ""))

    msg_lines = [
        f"{badge} {emoji} <b>[{category}]</b>",
        "━━━━━━━━━━━━━━━━━━━━",
        f"📌 <b>Notice</b>: {title}",
        f"🏛️ <b>Source</b>: {source}",
    ]
    if pub_date:
        msg_lines.append(f"📅 <b>Date</b>: {pub_date}")

    msg_lines.extend([
        "",
        f"🔗 <b>Direct Link / Notice</b>:\n{url}",
        "━━━━━━━━━━━━━━━━━━━━",
        "🤖 <i>Mera Exam Bot • Realtime Admissions Alert</i>"
    ])

    return "\n".join(msg_lines)


def format_digest_message(articles: List[Dict[str, Any]]) -> str:
    """
    Format multiple articles into a clean consolidated digest in HTML format.
    """
    if not articles:
        return "ℹ️ <b>Mera Exam Bot</b>: No new exam notifications at this moment."

    if len(articles) == 1:
        return format_single_article_message(articles[0])

    lines = [
        f"🎓 <b>EDUALERT: {len(articles)} NEW ADMISSIONS NOTICES</b>",
        "━━━━━━━━━━━━━━━━━━━━"
    ]

    for idx, art in enumerate(articles, 1):
        cat = html.escape(art.get("exam_category", "EXAM").upper())
        emoji = get_exam_emoji(cat)
        title = html.escape(art.get("title", "").strip())
        url = art.get("url", "").strip()

        lines.append(f"<b>{idx}.</b> {emoji} <b>[{cat}]</b> {title}")
        lines.append(f"   🔗 {url}\n")

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("🤖 <i>Mera Exam Bot • 24/7 Live Monitoring</i>")

    return "\n".join(lines)
