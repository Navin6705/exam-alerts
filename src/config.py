import json
import os
from pathlib import Path
from typing import Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEFAULT_CONFIG: Dict[str, Any] = {
    "whatsapp_provider": "telegram",
    "telegram": {
        "bot_token": "",
        "chat_id": ""
    },
    "gemini": {
        "api_key": ""
    },
    "callmebot": {
        "phone": "",
        "apikey": ""
    },
    "twilio": {
        "account_sid": "",
        "auth_token": "",
        "from_number": "whatsapp:+14155238886",
        "to_number": ""
    },
    "meta": {
        "phone_number_id": "",
        "access_token": "",
        "recipient_phone": ""
    },
    "monitored_exams": [
        "NTA",
        "NTA_TWITTER",
        "JEE",
        "JEE_ADV",
        "NEET",
        "VITEEE",
        "CUET",
        "ACPC",
        "GUJCET",
        "GSEB",
        "NIRMA",
        "DAIICT",
        "PDPU",
        "ADANI",
        "MHT_CET",
        "COMEDK",
        "MET",
        "WBJEE",
        "GSAUCA",
        "JAC",
        "JOSAA_CSAB",
        "IIIT_BANGALORE",
        "IIIT_HYDERABAD",
        "CHARUSAT",
        "LNMIIT",
        "THAPAR",
        "SRM_AEEE",
        "GUJARAT_TOP"
    ],
    "custom_keywords": [
        "Admit Card",
        "Exam Date",
        "Answer Key",
        "Result",
        "Application",
        "Registration",
        "Counselling"
    ],
    "polling_interval_minutes": 30,
    "enabled_sources": {
        "google_news": True,
        "nta_official": True,
        "viteee_official": True,
        "portals": True
    },
    "max_alerts_per_run": 5,
    "dry_run": False
}

CONFIG_FILE_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json, merging with defaults and env variables."""
    cfg = DEFAULT_CONFIG.copy()
    if CONFIG_FILE_PATH.exists():
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            for k, v in user_config.items():
                if isinstance(v, dict) and k in cfg and isinstance(cfg[k], dict):
                    cfg[k] = {**cfg[k], **v}
                else:
                    cfg[k] = v
        except Exception as e:
            print(f"[Config] Error loading {CONFIG_FILE_PATH}: {e}. Using defaults.")

    # Environment variables override (Useful for GitHub Actions Secrets & .env)
    if os.getenv("WHATSAPP_PROVIDER"):
        cfg["whatsapp_provider"] = os.environ["WHATSAPP_PROVIDER"]

    if os.getenv("TELEGRAM_BOT_TOKEN"):
        cfg["telegram"]["bot_token"] = os.environ["TELEGRAM_BOT_TOKEN"]
    if os.getenv("TELEGRAM_CHAT_ID"):
        cfg["telegram"]["chat_id"] = os.environ["TELEGRAM_CHAT_ID"]

    if os.getenv("GEMINI_API_KEY"):
        cfg["gemini"]["api_key"] = os.environ["GEMINI_API_KEY"]

    if os.getenv("CALLMEBOT_PHONE"):
        cfg["callmebot"]["phone"] = os.environ["CALLMEBOT_PHONE"]
    if os.getenv("CALLMEBOT_APIKEY"):
        cfg["callmebot"]["apikey"] = os.environ["CALLMEBOT_APIKEY"]

    if os.getenv("TWILIO_ACCOUNT_SID"):
        cfg["twilio"]["account_sid"] = os.environ["TWILIO_ACCOUNT_SID"]
    if os.getenv("TWILIO_AUTH_TOKEN"):
        cfg["twilio"]["auth_token"] = os.environ["TWILIO_AUTH_TOKEN"]
    if os.getenv("TWILIO_FROM_NUMBER"):
        cfg["twilio"]["from_number"] = os.environ["TWILIO_FROM_NUMBER"]
    if os.getenv("TWILIO_TO_NUMBER"):
        cfg["twilio"]["to_number"] = os.environ["TWILIO_TO_NUMBER"]

    if os.getenv("META_PHONE_NUMBER_ID"):
        cfg["meta"]["phone_number_id"] = os.environ["META_PHONE_NUMBER_ID"]
    if os.getenv("META_ACCESS_TOKEN"):
        cfg["meta"]["access_token"] = os.environ["META_ACCESS_TOKEN"]
    if os.getenv("META_RECIPIENT_PHONE"):
        cfg["meta"]["recipient_phone"] = os.environ["META_RECIPIENT_PHONE"]

    if os.getenv("DRY_RUN"):
        cfg["dry_run"] = os.getenv("DRY_RUN").lower() in ("true", "1", "yes")

    return cfg


def save_config(config_data: Dict[str, Any]) -> bool:
    """Save configuration to config.json."""
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Config] Error saving config: {e}")
        return False
