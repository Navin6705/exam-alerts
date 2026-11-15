from typing import Tuple
from .base import BaseWhatsAppDispatcher


class ConsoleDispatcher(BaseWhatsAppDispatcher):
    """Dry-run / Local testing dispatcher that prints formatted messages to console."""

    def __init__(self):
        pass

    def send_message(self, message: str) -> Tuple[bool, str]:
        print("\n" + "=" * 45)
        print("[CONSOLE DRY-RUN WHATSAPP DISPATCH]")
        print(message)
        print("=" * 45 + "\n")
        return True, "Message rendered in Console (Dry Run mode)"

    def test_connection(self) -> Tuple[bool, str]:
        return self.send_message("✅ [CONSOLE TEST] WhatsApp alert channel ready!")
