import os
from typing import Any, Dict
from .base import BaseWhatsAppDispatcher
from .callmebot import CallMeBotDispatcher
from .twilio_whatsapp import TwilioWhatsAppDispatcher
from .meta_whatsapp import MetaWhatsAppDispatcher
from .telegram_dispatcher import TelegramDispatcher
from .console_dispatcher import ConsoleDispatcher


def get_dispatcher(config: Dict[str, Any]) -> BaseWhatsAppDispatcher:
    """Factory to retrieve appropriate dispatcher based on config."""
    if config.get("dry_run", False):
        return ConsoleDispatcher()

    provider = config.get("whatsapp_provider", "telegram").lower()

    if provider == "telegram":
        tg = config.get("telegram", {})
        token = os.getenv("TELEGRAM_BOT_TOKEN") or tg.get("bot_token", "")
        chat_id = os.getenv("TELEGRAM_CHAT_ID") or tg.get("chat_id", "")
        return TelegramDispatcher(bot_token=token, chat_id=chat_id)
    elif provider == "callmebot":
        cmb = config.get("callmebot", {})
        return CallMeBotDispatcher(phone=cmb.get("phone", ""), apikey=cmb.get("apikey", ""))
    elif provider == "twilio":
        tw = config.get("twilio", {})
        return TwilioWhatsAppDispatcher(
            account_sid=tw.get("account_sid", ""),
            auth_token=tw.get("auth_token", ""),
            from_number=tw.get("from_number", ""),
            to_number=tw.get("to_number", "")
        )
    elif provider == "meta":
        meta = config.get("meta", {})
        return MetaWhatsAppDispatcher(
            phone_number_id=meta.get("phone_number_id", ""),
            access_token=meta.get("access_token", ""),
            recipient_phone=meta.get("recipient_phone", "")
        )
    elif provider == "console":
        return ConsoleDispatcher()
    else:
        print(f"[Dispatcher] Unknown provider '{provider}', falling back to Console.")
        return ConsoleDispatcher()
