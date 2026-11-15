from abc import ABC, abstractmethod
from typing import Tuple


class BaseWhatsAppDispatcher(ABC):
    """Abstract base class for WhatsApp delivery providers."""

    @abstractmethod
    def send_message(self, message: str) -> Tuple[bool, str]:
        """
        Send message to WhatsApp.
        Returns:
            Tuple[bool, str]: (Success boolean, Response or error message)
        """
        pass

    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test WhatsApp delivery by sending a quick verification ping.
        """
        pass
