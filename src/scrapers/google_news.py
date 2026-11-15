import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List

EXAM_QUERIES = {
    # 1. Central / National Exams
    "NTA": "NTA National Testing Agency exam announcement OR notice when:2d",
    "NTA_TWITTER": "NTA_Exams OR National Testing Agency tweet OR notice when:2d",
    "JEE": "JEE Main exam admit card OR registration OR dates when:2d",
    "JEE_ADV": "JEE Advanced registration OR eligibility OR exam date IIT when:2d",
    "NEET": "NEET UG exam admit card OR counselling OR registration when:2d",
    "CUET": "CUET UG exam dates OR application form OR registration when:2d",
    "VITEEE": "VITEEE Vellore Institute exam application OR slot booking when:3d",

    # 2. Gujarat Engineering & State Boards
    "ACPC": "ACPC Gujarat BTech engineering admission notification when:3d",
    "GUJCET": "GUJCET exam dates OR result OR merit list ACPC when:3d",
    "GSEB": "GSEB HSC 12th science board exam dates OR result when:3d",
    "GSAUCA": "GSAUCA Gujarat agriculture admission merit list when:3d",

    # 3. Top Gujarat Universities
    "NIRMA": "Nirma University BTech engineering admission when:3d",
    "DAIICT": "DAIICT BTech admission cut off dates when:3d",
    "PDPU": "PDPU OR PDEU BTech admission dates merit list when:3d",
    "ADANI": "Adani University BTech engineering admission when:3d",

    # 4. State & Other Major Engineering Entrances
    "MHT_CET": "MHT CET engineering admission counselling seat allotment when:3d",
    "COMEDK": "COMEDK UGET engineering application admit card dates when:3d",
    "MET": "MET Manipal Entrance Test BTech application dates when:3d",
    "WBJEE": "WBJEE engineering entrance exam admit card result when:3d",
    "BITSAT": "BITSAT Birla Institute entrance exam dates OR registration when:3d",

    # 5. Premier National Engineering Entrances & Counselling
    "JAC": "JAC Delhi BTech counselling registration OR seat allotment OR JAC Chandigarh when:3d",
    "JOSAA_CSAB": "JoSAA counselling seat allotment OR CSAB round IIT NIT BTech when:3d",
    "IIIT_BANGALORE": "IIIT Bangalore BTech admission OR cutoff OR merit list when:3d",
    "IIIT_HYDERABAD": "IIIT Hyderabad BTech admission OR UGEE exam OR cutoff when:3d",
    "CHARUSAT": "CHARUSAT University Changa admission OR CSPIT BTech ACPC when:3d",
    "LNMIIT": "LNMIIT Jaipur admission BTech OR cutoff application when:3d",
    "THAPAR": "Thapar University BTech admission counselling dates when:3d",
    "SRM_AEEE": "SRMJEEE OR AEEE Amrita BTech entrance exam dates when:3d",
    "GUJARAT_TOP": "LD College of Engineering LDCE OR DDU Nadiad BTech admission when:3d"
}


def fetch_google_news_for_query(query: str, exam_category: str) -> List[Dict[str, Any]]:
    """Fetch and parse Google News RSS for a given search query."""
    encoded_q = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=en-IN&gl=IN&ceid=IN:en"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    req = urllib.request.Request(rss_url, headers=headers)
    results = []

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            items = root.findall(".//item")
            
            for item in items:
                title_elem = item.find("title")
                link_elem = item.find("link")
                pub_elem = item.find("pubDate")
                source_elem = item.find("source")

                if title_elem is None or link_elem is None:
                    continue

                raw_title = title_elem.text or ""
                link = link_elem.text or ""
                pub_date = pub_elem.text if pub_elem is not None else datetime.now().isoformat()
                source_name = source_elem.text if source_elem is not None else "Google News"

                # Clean title: often titles end with " - Source Name"
                clean_title = raw_title
                if " - " in clean_title:
                    clean_title = clean_title.rsplit(" - ", 1)[0].strip()

                results.append({
                    "title": clean_title,
                    "url": link,
                    "source": f"News ({source_name})",
                    "exam_category": exam_category,
                    "published_date": pub_date
                })
    except Exception as e:
        print(f"[GoogleNews] Error fetching query '{query}': {e}")

    return results


def fetch_all_google_news(monitored_exams: List[str]) -> List[Dict[str, Any]]:
    """Fetch Google News for all configured exams and institutions."""
    all_articles = []
    for exam in monitored_exams:
        exam_key = exam.upper()
        query = EXAM_QUERIES.get(exam_key, f"{exam} admission notification when:2d")
        items = fetch_google_news_for_query(query, exam_key)
        all_articles.extend(items)
    return all_articles
