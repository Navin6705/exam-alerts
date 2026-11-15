from typing import Tuple
import requests
from .base import BaseWhatsAppDispatcher


class TwilioWhatsAppDispatcher(BaseWhatsAppDispatcher):
    """Twilio WhatsApp Dispatcher using standard Twilio REST API."""

    def __init__(self, account_sid: str, auth_token: str, from_number: str, to_number: str):
        self.account_sid = account_sid.strip()
        self.auth_token = auth_token.strip()
        self.from_number = from_number.strip()
        self.to_number = to_number.strip()

    def send_message(self, message: str) -> Tuple[bool, str]:
        if not (self.account_sid and self.auth_token and self.to_number):
            return False, "Twilio is not configured. Missing account_sid, auth_token, or to_number."

        from_num = self.from_number if self.from_number.startswith("whatsapp:") else f"whatsapp:{self.from_number}"
        to_num = self.to_number if self.to_number.startswith("whatsapp:") else f"whatsapp:{self.to_number}"

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        data = {
            "From": from_num,
            "To": to_num,
            "Body": message
        }

        try:
            resp = requests.post(url, data=data, auth=(self.account_sid, self.auth_token), timeout=15)
            if resp.status_code in (200, 201):
                sid = resp.json().get("sid", "OK")
                return True, f"Twilio Message Sent (SID: {sid})"
            else:
                err_msg = resp.json().get("message", resp.text)
                return False, f"Twilio Error ({resp.status_code}): {err_msg}"
        except Exception as e:
            return False, f"Twilio request exception: {e}"

    def test_connection(self) -> Tuple[bool, str]:
        test_msg = "✅ *EduAlert Test Message*\nTwilio WhatsApp Integration is working! You will receive JEE/NEET/NTA/VITEEE alerts here. 🎓"
        return self.send_message(test_msg)
