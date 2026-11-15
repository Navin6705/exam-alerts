import re
from datetime import datetime
from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

VITEEE_URL = "https://viteee.vit.ac.in/"


def fetch_viteee_official_notices() -> List[Dict[str, Any]]:
    """Scrape official notices and announcements from the official VITEEE portal."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    results = []
    try:
        resp = requests.get(VITEEE_URL, headers=headers, verify=False, timeout=12)
        if resp.status_code != 200:
            print(f"[VITEEE Scraper] Failed to fetch VITEEE portal: HTTP {resp.status_code}")
            return results

        soup = BeautifulSoup(resp.text, "html.parser")

        # Check announcements, marquees, notices, alerts
        notice_elements = soup.find_all(
            ["marquee", "div", "p", "a"],
            class_=lambda c: c and any(k in str(c).lower() for k in ["notice", "alert", "announcement", "important", "date", "marquee"])
        )

        for elem in notice_elements:
            text = elem.get_text(" ", strip=True)
            text = re.sub(r"\s+", " ", text).strip()

            if len(text) < 15 or len(text) > 350:
                continue

            # Extract any link
            a_tag = elem if elem.name == "a" else elem.find("a")
            href = a_tag.get("href", "").strip() if a_tag else ""

            if href.startswith("/"):
                url = f"https://viteee.vit.ac.in{href}"
            elif href.startswith("http"):
                url = href
            else:
                url = VITEEE_URL

            # Clean click here text
            clean_text = re.sub(r"\b(Click here|Read More|Apply Now)\b", "", text, flags=re.IGNORECASE).strip()

            results.append({
                "title": f"[VITEEE OFFICIAL] {clean_text}",
                "url": url,
                "source": "Official VIT Portal (viteee.vit.ac.in)",
                "exam_category": "VITEEE",
                "published_date": datetime.now().strftime("%Y-%m-%d")
            })

    except Exception as e:
        print(f"[VITEEE Scraper] Exception: {e}")

    # Deduplicate in batch
    unique_items = []
    seen = set()
    for item in results:
        key = item["title"][:60]
        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    return unique_items
