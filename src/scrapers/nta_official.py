import re
from datetime import datetime
from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

NTA_BASE_URL = "https://nta.ac.in"


def fetch_nta_official_notices() -> List[Dict[str, Any]]:
    """Scrape official public notices from the official NTA website (nta.ac.in)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    }

    results = []
    try:
        resp = requests.get(NTA_BASE_URL, headers=headers, verify=False, timeout=12)
        if resp.status_code != 200:
            print(f"[NTA Scraper] Failed to fetch NTA: HTTP {resp.status_code}")
            return results

        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Look for notice anchors pointing to PDFs or notices
        for a in soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            if not href:
                continue

            # We are interested in notice PDFs or notice links
            is_notice = "/Download/Notice/" in href or "notice" in href.lower() or href.lower().endswith(".pdf")
            if not is_notice:
                continue

            # Retrieve descriptive text from anchor or parent element
            text = a.get_text(" ", strip=True)
            if not text or len(text) < 10 or text.lower() in ("read more", "click here", "download"):
                parent = a.find_parent(["li", "p", "div", "tr"])
                if parent:
                    text = parent.get_text(" ", strip=True)

            # Clean up text
            text = re.sub(r"\s+", " ", text).strip()
            text = re.sub(r"Read More\b", "", text, flags=re.IGNORECASE).strip()

            if len(text) < 12:
                continue

            # Resolve absolute URL
            if href.startswith("/"):
                full_url = f"{NTA_BASE_URL}{href}"
            elif not href.startswith("http"):
                full_url = f"{NTA_BASE_URL}/{href}"
            else:
                full_url = href

            # Categorize by exam
            text_upper = text.upper()
            if "JEE" in text_upper:
                category = "JEE"
            elif "NEET" in text_upper:
                category = "NEET"
            elif "CUET" in text_upper:
                category = "CUET"
            else:
                category = "NTA"

            # Parse date if available in URL (e.g. Notice_20261114192445.pdf)
            date_match = re.search(r"Notice_(\d{4})(\d{2})(\d{2})", href)
            if date_match:
                pub_date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            else:
                pub_date = datetime.now().strftime("%Y-%m-%d")

            results.append({
                "title": f"[OFFICIAL NTA NOTICE] {text}",
                "url": full_url,
                "source": "Official NTA Portal (nta.ac.in)",
                "exam_category": category,
                "published_date": pub_date
            })

    except Exception as e:
        print(f"[NTA Scraper] Exception: {e}")

    # Deduplicate within this single scrape batch
    unique_items = []
    seen_urls = set()
    for item in results:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            unique_items.append(item)

    return unique_items
