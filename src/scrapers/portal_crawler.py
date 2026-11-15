import re
from datetime import datetime
from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

MONITORED_PORTALS = [
    {
        "name": "ACPC Gujarat",
        "category": "ACPC",
        "url": "https://gujacpc.admissions.nic.in/",
        "base_url": "https://gujacpc.admissions.nic.in",
        "keywords": ["b.tech", "engineering", "cutoff", "merit", "registration", "round", "allotment", "guidelines", "schedule"]
    },
    {
        "name": "JEE Advanced",
        "category": "JEE_ADV",
        "url": "https://jeeadv.ac.in/",
        "base_url": "https://jeeadv.ac.in",
        "keywords": ["registration", "eligibility", "syllabus", "admit card", "examination", "important dates", "brochure"]
    },
    {
        "name": "Nirma University B.Tech",
        "category": "NIRMA",
        "url": "https://technology.nirmauni.ac.in/admission-aid/b-tech/",
        "base_url": "https://technology.nirmauni.ac.in",
        "keywords": ["b.tech", "admission", "application", "all-india", "gujcet", "merit", "counselling", "eligibility"]
    },
    {
        "name": "DA-IICT Admissions",
        "category": "DAIICT",
        "url": "https://www.daiict.ac.in/admissions",
        "base_url": "https://www.daiict.ac.in",
        "keywords": ["b.tech", "admission", "all-india", "gujcet", "ict", "application", "merit", "undergraduate"]
    },
    {
        "name": "PDPU / PDEU Admissions",
        "category": "PDPU",
        "url": "https://www.pdeu.ac.in/",
        "base_url": "https://www.pdeu.ac.in",
        "keywords": ["b.tech", "admission", "application", "merit", "counselling", "round", "btech"]
    },
    {
        "name": "Adani University B.Tech",
        "category": "ADANI",
        "url": "https://www.adaniuni.ac.in/",
        "base_url": "https://www.adaniuni.ac.in",
        "keywords": ["b.tech", "admission", "engineering", "apply", "scholarship", "dates", "btech"]
    },
    {
        "name": "COMEDK UGET",
        "category": "COMEDK",
        "url": "https://www.comedk.org/",
        "base_url": "https://www.comedk.org",
        "keywords": ["uget", "application", "admit card", "exam date", "counselling", "seat allotment"]
    },
    {
        "name": "WBJEE Portal",
        "category": "WBJEE",
        "url": "https://wbjeeb.nic.in/",
        "base_url": "https://wbjeeb.nic.in",
        "keywords": ["wbjee", "information bulletin", "registration", "admit card", "result", "counselling"]
    },
    {
        "name": "JAC Delhi Admissions",
        "category": "JAC",
        "url": "https://jacdelhi.admissions.nic.in/",
        "base_url": "https://jacdelhi.admissions.nic.in",
        "keywords": ["b.tech", "counselling", "seat allotment", "merit", "schedule", "registration", "round", "dtu", "nsut", "iiitd"]
    },
    {
        "name": "IIIT Bangalore B.Tech",
        "category": "IIIT_BANGALORE",
        "url": "https://www.iiitb.ac.in/",
        "base_url": "https://www.iiitb.ac.in",
        "keywords": ["b.tech", "admission", "application", "jee main", "merit list", "counselling", "round", "integrated m.tech"]
    },
    {
        "name": "IIIT Hyderabad UG Admissions",
        "category": "IIIT_HYDERABAD",
        "url": "https://ugadmissions.iiit.ac.in/",
        "base_url": "https://ugadmissions.iiit.ac.in",
        "keywords": ["b.tech", "ugee", "jee", "admission", "application", "portal", "dates", "interview", "spec"]
    },
    {
        "name": "CHARUSAT University Changa",
        "category": "CHARUSAT",
        "url": "https://charusat.ac.in/",
        "base_url": "https://charusat.ac.in",
        "keywords": ["b.tech", "admission", "gujcet", "engineering", "acpc", "cspit", "depstar", "application", "changa"]
    },
    {
        "name": "JoSAA / CSAB Counselling",
        "category": "JOSAA_CSAB",
        "url": "https://josaa.nic.in/",
        "base_url": "https://josaa.nic.in",
        "keywords": ["counselling", "seat allotment", "opening", "closing", "rank", "schedule", "business rules", "round", "csab"]
    },
    {
        "name": "BITS Pilani Admissions",
        "category": "BITSAT",
        "url": "https://www.bitsadmission.com/",
        "base_url": "https://www.bitsadmission.com",
        "keywords": ["bitsat", "admission", "b.e", "application", "iteration", "scorecard", "dates", "pilani"]
    },
    {
        "name": "LNMIIT Jaipur Admissions",
        "category": "LNMIIT",
        "url": "https://lnmiit.ac.in/",
        "base_url": "https://lnmiit.ac.in",
        "keywords": ["b.tech", "admission", "application", "merit", "round", "counselling", "jee main", "lnmiit"]
    },
    {
        "name": "Thapar Institute Patiala",
        "category": "THAPAR",
        "url": "https://www.thapar.edu/",
        "base_url": "https://www.thapar.edu",
        "keywords": ["b.tech", "admission", "application", "counselling", "merit", "cutoff", "jee", "tiet"]
    },
    {
        "name": "DDU Nadiad B.Tech",
        "category": "GUJARAT_TOP",
        "url": "https://www.ddu.ac.in/",
        "base_url": "https://www.ddu.ac.in",
        "keywords": ["b.tech", "admission", "acpc", "engineering", "merit", "dharamsinh"]
    },
    {
        "name": "LDCE Ahmedabad B.Tech",
        "category": "GUJARAT_TOP",
        "url": "http://ldce.ac.in/",
        "base_url": "http://ldce.ac.in",
        "keywords": ["b.tech", "admission", "acpc", "engineering", "merit", "counselling", "ldce"]
    }
]


def crawl_official_portals() -> List[Dict[str, Any]]:
    """Crawl official college and exam portals for notices, announcements, and PDFs."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    discovered = []

    for portal in MONITORED_PORTALS:
        try:
            resp = requests.get(portal["url"], headers=headers, verify=False, timeout=10)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            anchors = soup.find_all("a", href=True)

            for a in anchors:
                href = a.get("href", "").strip()
                text = a.get_text(" ", strip=True)

                if not text or len(text) < 12 or len(text) > 250:
                    continue

                # Filter out mailto, tel, javascript, anchors
                if href.startswith(("mailto:", "tel:", "javascript:", "#")):
                    continue

                text_lower = text.lower()
                href_lower = href.lower()

                # Check if matches any of the portal keywords or is a PDF
                is_match = any(k in text_lower for k in portal["keywords"]) or ".pdf" in href_lower

                if not is_match:
                    continue

                # Filter out generic navigation links
                if text_lower in ("home", "about us", "contact us", "read more", "apply now", "click here", "download", "privacy policy"):
                    continue

                # Resolve full URL
                if href.startswith("/"):
                    full_url = f"{portal['base_url']}{href}"
                elif not href.startswith("http"):
                    full_url = f"{portal['base_url']}/{href}"
                else:
                    full_url = href

                clean_title = re.sub(r"\s+", " ", text).strip()

                discovered.append({
                    "title": f"[{portal['name'].upper()}] {clean_title}",
                    "url": full_url,
                    "source": f"Official Portal ({portal['name']})",
                    "exam_category": portal["category"],
                    "published_date": datetime.now().strftime("%Y-%m-%d")
                })
        except Exception as e:
            print(f"[Portal Crawler] Error checking {portal['name']}: {e}")

    # Deduplicate in batch
    unique_items = []
    seen = set()
    for item in discovered:
        key = item["url"]
        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    return unique_items
