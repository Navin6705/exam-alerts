from typing import Tuple, Optional, List
import requests
from .base import BaseWhatsAppDispatcher

MAX_TELEGRAM_MSG_LEN = 3900


class TelegramDispatcher(BaseWhatsAppDispatcher):
    """
    Official Telegram Bot Dispatcher.
    Uses official Telegram Bot API (Zero risk of personal account logout).
    Supports:
    - Text messages with Markdown / HTML (with automatic chunking if >4000 chars)
    - Sending documents / PDFs directly with captions
    - Action buttons
    """

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token.strip()
        self.chat_id = str(chat_id).strip()
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, message: str, parse_mode: str = "Markdown") -> Tuple[bool, str]:
        if not self.bot_token:
            return False, "Telegram Bot Token is missing."
        if not self.chat_id:
            return False, "Telegram Chat ID is missing. Please start the bot in Telegram first."

        # If message is longer than Telegram limit (4096), split cleanly on newlines
        if len(message) > MAX_TELEGRAM_MSG_LEN:
            chunks = self._split_message(message, MAX_TELEGRAM_MSG_LEN)
            overall_success = True
            last_resp = ""
            for chunk in chunks:
                ok, resp = self._send_single_chunk(chunk, parse_mode)
                if not ok:
                    overall_success = False
                last_resp = resp
            return overall_success, last_resp

        return self._send_single_chunk(message, parse_mode)

    def _send_single_chunk(self, text: str, parse_mode: str = "Markdown") -> Tuple[bool, str]:
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }

        try:
            resp = requests.post(url, json=payload, timeout=15)
            data = resp.json()
            if data.get("ok"):
                return True, f"Telegram message sent to chat {self.chat_id}"
            else:
                # If markdown fails due to special chars, retry in plain text
                if parse_mode == "Markdown":
                    payload.pop("parse_mode", None)
                    retry_resp = requests.post(url, json=payload, timeout=15)
                    retry_data = retry_resp.json()
                    if retry_data.get("ok"):
                        return True, f"Telegram message sent (plain text) to {self.chat_id}"
                return False, f"Telegram API Error: {data.get('description', resp.text)}"
        except Exception as e:
            return False, f"Telegram connection error: {e}"

    def _split_message(self, text: str, max_len: int) -> List[str]:
        """Split text into chunks on newline boundaries."""
        chunks = []
        current = []
        current_len = 0

        for line in text.split("\n"):
            line_len = len(line) + 1
            if current_len + line_len > max_len:
                if current:
                    chunks.append("\n".join(current))
                    current = [line]
                    current_len = line_len
                else:
                    # Single line longer than max_len
                    chunks.append(line[:max_len])
                    current = [line[max_len:]]
                    current_len = len(current[0])
            else:
                current.append(line)
                current_len += line_len

        if current:
            chunks.append("\n".join(current))
        return chunks

    def send_document(self, document_url: str, caption: str = "") -> Tuple[bool, str]:
        """Send a PDF or document file link directly to Telegram."""
        if not self.bot_token or not self.chat_id:
            return False, "Missing bot_token or chat_id"

        url = f"{self.base_url}/sendDocument"
        payload = {
            "chat_id": self.chat_id,
            "document": document_url,
            "caption": caption[:1024]
        }

        try:
            resp = requests.post(url, json=payload, timeout=25)
            data = resp.json()
            if data.get("ok"):
                return True, f"Document sent to Telegram chat {self.chat_id}"
            else:
                return False, f"Telegram sendDocument Error: {data.get('description')}"
        except Exception as e:
            return False, f"Telegram sendDocument Exception: {e}"

    def test_connection(self) -> Tuple[bool, str]:
        test_msg = "🎓 *Mera Exam Bot Connected Successfully!*\n\nAapko NTA, JEE Main/Adv, NEET, aur VITEEE ke official circulars aur AI summaries yahan receive honge! 🚀"
        return self.send_message(test_msg)

    def get_latest_chat_id(self) -> Optional[str]:
        """Helper to discover user's chat_id after they press /start."""
        try:
            resp = requests.get(f"{self.base_url}/getUpdates", timeout=10)
            data = resp.json()
            if data.get("ok") and data.get("result"):
                last_msg = data["result"][-1]
                chat = last_msg.get("message", {}).get("chat", {})
                return str(chat.get("id"))
        except Exception as e:
            print(f"[Telegram] Error fetching updates: {e}")
        return None
