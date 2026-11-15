import urllib.parse
from typing import Tuple
import requests
from .base import BaseWhatsAppDispatcher


class CallMeBotDispatcher(BaseWhatsAppDispatcher):
    """
    CallMeBot WhatsApp Dispatcher.
    Completely free and easiest setup for personal WhatsApp notifications.
    Setup steps:
    1. Add +34 644 44 49 48 to WhatsApp contacts (CallMeBot)
    2. Send message: 'I allow callmebot to send me messages'
    3. You will receive: 'API Activated. Your apiKey is: XXXXXX'
    """

    def __init__(self, phone: str, apikey: str):
        self.phone = phone.strip()
        # Ensure proper format: remove spaces and hyphens
        self.phone = self.phone.replace(" ", "").replace("-", "")
        self.apikey = apikey.strip()

    def send_message(self, message: str) -> Tuple[bool, str]:
        if not self.phone or not self.apikey:
            return False, "CallMeBot is not configured. Please enter your Phone Number and API Key in config/dashboard."

        # Format phone: ensure international prefix (e.g. +91)
        phone = self.phone
        if not phone.startswith("+"):
            phone = f"+{phone}"

        encoded_text = urllib.parse.quote(message)
        # CallMeBot accepts GET request
        api_url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_text}&apikey={self.apikey}"

        try:
            resp = requests.get(api_url, timeout=15)
            if resp.status_code == 200 and ("Message queued" in resp.text or "success" in resp.text.lower() or resp.text.strip() == ""):
                return True, f"Delivered to WhatsApp ({phone}): {resp.text[:100]}"
            elif "not registered" in resp.text.lower() or "invalid" in resp.text.lower():
                return False, f"CallMeBot Auth Error: {resp.text.strip()} (Check API Key or send 'I allow callmebot to send me messages' to +34 644 44 49 48)"
            else:
                return False, f"CallMeBot response ({resp.status_code}): {resp.text[:200]}"
        except Exception as e:
            return False, f"Network error calling CallMeBot: {e}"

    def test_connection(self) -> Tuple[bool, str]:
        test_msg = "✅ *EduAlert Test Message*\nYour WhatsApp alerts for NTA, JEE, NEET, and VITEEE are successfully connected! 🎓"
        return self.send_message(test_msg)
