import re
from typing import Dict, Any, Optional
import requests
import urllib3
try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None

urllib3.disable_warnings()


def extract_pdf_content(pdf_url: str) -> Optional[str]:
    """Download PDF and extract text using PyMuPDF."""
    if pymupdf is None:
        return None
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(pdf_url, headers=headers, verify=False, timeout=15)
        if resp.status_code != 200 or not resp.content:
            return None

        doc = pymupdf.open(stream=resp.content, filetype="pdf")
        full_text = []
        for page in doc:
            full_text.append(page.get_text())
        
        extracted = "\n".join(full_text).strip()
        return extracted if len(extracted) > 50 else None
    except Exception as e:
        print(f"[PDF Analyzer] Error extracting {pdf_url}: {e}")
        return None


def extract_deep_notice_summary(raw_text: str, fallback_title: str) -> Dict[str, Any]:
    """
    Intelligently parse NTA / exam notice text to extract subject, dates, rules, and core points.
    """
    lines_raw = [l.strip() for l in raw_text.splitlines() if l.strip()]

    # 1. Subject extraction
    subject_match = re.search(r"Subject:\s*([^\n]+(?:\n[^\n]+)?)", raw_text, re.IGNORECASE)
    subject = subject_match.group(1).strip() if subject_match else fallback_title
    subject = re.sub(r"\s+", " ", subject)

    # 2. Date extraction
    date_match = re.search(r"Dated?:\s*([0-9\.\-/]+)", raw_text, re.IGNORECASE)
    notice_date = date_match.group(1).strip() if date_match else ""

    # 3. Find key deadlines / dates in the document
    date_patterns = [
        r"(?:on or before|last date|from|upto)\s*([0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+[0-9]{4}[^\.\n]*)",
        r"([0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4}\s*(?:to|-)\s*[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4})",
        r"([0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+[0-9]{4}\s*(?:to|-)?\s*[0-9]{1,2}?(?:st|nd|rd|th)?\s*[A-Za-z]*\s*[0-9]{4}?)"
    ]
    extracted_dates = []
    for pat in date_patterns:
        for match in re.finditer(pat, raw_text, re.IGNORECASE):
            d_str = re.sub(r"\s+", " ", match.group(0).strip())
            if len(d_str) > 6 and d_str not in extracted_dates:
                extracted_dates.append(d_str)

    # 4. Extract core decision / rule paragraphs
    # Join into coherent paragraphs
    normalized_text = re.sub(r"\n{2,}", "\n\n", raw_text)
    raw_paragraphs = normalized_text.split("\n\n")
    if len(raw_paragraphs) < 3:
        # Split on sentence boundaries if newlines were sparse
        raw_paragraphs = re.split(r"(?<=\.)\s+", raw_text)

    action_points = []
    for p in raw_paragraphs:
        clean_p = re.sub(r"\s+", " ", p).strip()
        if len(clean_p) < 35 or len(clean_p) > 400:
            continue
        # Skip headers / addresses
        if any(h in clean_p.lower() for h in ["autonomous organization", "minto road", "press building", "department of higher education", "telephone:"]):
            continue
        # Filter for action keywords
        if any(k in clean_p.lower() for k in [
            "decided to", "valid", "fresh application", "last date", "fee",
            "correction", "admit card", "examination", "eligible", "allowed", "instructions", "schedule"
        ]):
            if clean_p not in action_points and not clean_p.lower().startswith("subject:"):
                action_points.append(clean_p)

    # 5. Extract helpline / contact info if available
    helpline_match = re.search(r"(?:contact|help desk|email)[^\.\n]*(?:011-[0-9]+|[a-z0-9_\.-]+@[a-z0-9_\.-]+)", raw_text, re.IGNORECASE)
    helpline = helpline_match.group(0).strip() if helpline_match else ""

    return {
        "subject": subject,
        "notice_date": notice_date,
        "key_dates": extracted_dates[:4],
        "core_points": action_points[:4],
        "helpline": helpline
    }
