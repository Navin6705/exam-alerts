from typing import Tuple
import requests
from .base import BaseWhatsAppDispatcher


class MetaWhatsAppDispatcher(BaseWhatsAppDispatcher):
    """Official Meta / WhatsApp Cloud API Dispatcher."""

    def __init__(self, phone_number_id: str, access_token: str, recipient_phone: str):
        self.phone_number_id = phone_number_id.strip()
        self.access_token = access_token.strip()
        self.recipient_phone = recipient_phone.strip().replace("+", "").replace(" ", "")

    def send_message(self, message: str) -> Tuple[bool, str]:
        if not (self.phone_number_id and self.access_token and self.recipient_phone):
            return False, "Meta WhatsApp API is not configured. Missing phone_number_id, access_token, or recipient_phone."

        url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": self.recipient_phone,
            "type": "text",
            "text": {
                "body": message
            }
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            if resp.status_code in (200, 201):
                return True, "Meta WhatsApp Cloud API delivered successfully."
            else:
                return False, f"Meta API Error ({resp.status_code}): {resp.text[:200]}"
        except Exception as e:
            return False, f"Meta API request exception: {e}"

    def test_connection(self) -> Tuple[bool, str]:
        test_msg = "✅ *EduAlert Test Message*\nMeta WhatsApp Cloud API is connected successfully! 🎓"
        return self.send_message(test_msg)
