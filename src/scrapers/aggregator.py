import re
from typing import Any, Dict, List
from ..database import save_article, compute_hash, is_article_seen
from .google_news import fetch_all_google_news
from .nta_official import fetch_nta_official_notices
from .viteee_official import fetch_viteee_official_notices
from .portal_crawler import crawl_official_portals

HIGH_PRIORITY_KEYWORDS = [
    "admit card", "hall ticket", "exam date", "dates announced",
    "answer key", "result announced", "cut off", "scorecard",
    "registration started", "registration ends", "last date extended",
    "counselling", "allotment", "postponed", "urgent", "corrigendum",
    "merit list", "seat matrix", "round 1", "round 2", "stray round"
]

MEDIUM_PRIORITY_KEYWORDS = [
    "application form", "registration", "syllabus", "eligibility",
    "exam pattern", "information bulletin", "mock test", "city intimation",
    "seats", "brochure", "guidelines", "b.tech", "admission"
]


def classify_priority(title: str) -> str:
    """Classify alert priority based on keywords in title."""
    lower_title = title.lower()
    for kw in HIGH_PRIORITY_KEYWORDS:
        if kw in lower_title:
            return "HIGH"
    for kw in MEDIUM_PRIORITY_KEYWORDS:
        if kw in lower_title:
            return "MEDIUM"
    return "LOW"


def run_full_aggregation(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Run all enabled scrapers (NTA, VITEEE, Portals, Google News),
    categorize, calculate priority, filter duplicates, and store new alerts.
    """
    monitored_exams = config.get("monitored_exams", [
        "NTA", "NTA_TWITTER", "JEE", "JEE_ADV", "NEET", "VITEEE", "CUET",
        "ACPC", "GUJCET", "GSEB", "NIRMA", "DAIICT", "PDPU", "ADANI",
        "MHT_CET", "COMEDK", "MET", "WBJEE", "GSAUCA"
    ])
    enabled_sources = config.get("enabled_sources", {})

    collected_raw: List[Dict[str, Any]] = []

    # 1. Official NTA Notices (nta.ac.in)
    if enabled_sources.get("nta_official", True):
        try:
            nta_items = fetch_nta_official_notices()
            collected_raw.extend(nta_items)
        except Exception as e:
            print(f"[Aggregator] Error in NTA official scraper: {e}")

    # 2. Official VITEEE Notices (viteee.vit.ac.in)
    if enabled_sources.get("viteee_official", True):
        try:
            viteee_items = fetch_viteee_official_notices()
            collected_raw.extend(viteee_items)
        except Exception as e:
            print(f"[Aggregator] Error in VITEEE official scraper: {e}")

    # 3. Direct Crawling for ACPC, JEE Adv, Nirma, DAIICT, PDPU, Adani, COMEDK, WBJEE
    try:
        portal_items = crawl_official_portals()
        collected_raw.extend(portal_items)
    except Exception as e:
        print(f"[Aggregator] Error crawling admission portals: {e}")

    # 4. Google News Feeds (Broad Coverage including NTA Twitter, Gujarat, State CETs)
    if enabled_sources.get("google_news", True):
        try:
            gnews_items = fetch_all_google_news(monitored_exams)
            collected_raw.extend(gnews_items)
        except Exception as e:
            print(f"[Aggregator] Error in Google News scraper: {e}")

    # Process and filter
    newly_saved: List[Dict[str, Any]] = []
    
    for item in collected_raw:
        title = item["title"].strip()
        url = item["url"].strip()
        category = item.get("exam_category", "GENERAL").upper()

        # Set priority
        priority = classify_priority(title)
        content_hash = compute_hash(title, url)

        # Check deduplication
        if is_article_seen(content_hash):
            continue

        article_record = {
            "content_hash": content_hash,
            "title": title,
            "url": url,
            "source": item.get("source", "Unknown"),
            "exam_category": category,
            "priority": priority,
            "published_date": item.get("published_date")
        }

        article_id = save_article(article_record)
        if article_id:
            article_record["id"] = article_id
            newly_saved.append(article_record)

    return newly_saved
