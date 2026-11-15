import argparse
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

from src.config import load_config
from src.database import (
    get_unsent_articles,
    init_db,
    log_dispatch,
    mark_article_sent,
)
from src.dispatchers import get_dispatcher
from src.formatters.message_formatter import format_digest_message, format_single_article_message
from src.ai.gemini_summarizer import generate_ai_exam_summary
from src.scrapers.aggregator import run_full_aggregation


def run_pipeline_once(config: Dict[str, Any] = None, send_as_digest: bool = False) -> Dict[str, Any]:
    """
    Execute one full cycle of scraping, deduplication, deep PDF/AI summarization,
    message dispatch, and PDF file attachment.
    """
    if config is None:
        config = load_config()

    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Starting Exam News Scan...")
    
    # 1. Scrape and store new items
    new_articles = run_full_aggregation(config)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📥 Found {len(new_articles)} new unseen articles.")

    # 2. Get pending unsent articles from DB
    max_batch = config.get("max_alerts_per_run", 5)
    pending_articles = get_unsent_articles(limit=max_batch)

    if not pending_articles:
        print("✅ No pending alerts to dispatch.")
        return {
            "new_scraped": len(new_articles),
            "dispatched": 0,
            "status": "NO_NEW_ALERTS",
            "message": "Scan complete. No new pending alerts to send."
        }

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📤 Dispatching {len(pending_articles)} alerts...")
    dispatcher = get_dispatcher(config)
    channel_name = config.get("whatsapp_provider", "telegram")
    
    recipient = (
        config.get("telegram", {}).get("chat_id")
        if channel_name == "telegram"
        else config.get("callmebot", {}).get("phone")
    )

    gemini_key = config.get("gemini", {}).get("api_key") or os.getenv("GEMINI_API_KEY", "")

    if send_as_digest and len(pending_articles) > 1:
        # Consolidated digest message
        message = format_digest_message(pending_articles)
        success, response_text = dispatcher.send_message(message)
        
        status_flag = "SENT" if success else "FAILED"
        for art in pending_articles:
            mark_article_sent(art["id"], status=status_flag, error_message=response_text if not success else None)
        
        log_dispatch(
            channel=channel_name,
            recipient=str(recipient),
            article_count=len(pending_articles),
            status="SUCCESS" if success else "FAILED",
            response_preview=response_text
        )

        return {
            "new_scraped": len(new_articles),
            "dispatched": len(pending_articles) if success else 0,
            "status": "SUCCESS" if success else "FAILED",
            "response": response_text
        }
    else:
        # Send deep individual analysis + actual PDF document
        dispatched_count = 0
        last_resp = ""
        for art in pending_articles:
            print(f"🔍 Analyzing circular & generating summary for: {art['title'][:50]}...")
            msg = generate_ai_exam_summary(art, gemini_key)

            # Step A: Send detailed message
            success, response_text = dispatcher.send_message(msg)
            last_resp = response_text
            status_flag = "SENT" if success else "FAILED"
            mark_article_sent(art["id"], status=status_flag, error_message=response_text if not success else None)
            
            # Step B: If article points to an official PDF, send the PDF document file too!
            is_pdf = art.get("url", "").lower().endswith(".pdf") or "/download/notice/" in art.get("url", "").lower()
            if success and is_pdf and hasattr(dispatcher, "send_document"):
                time.sleep(1.0)
                pdf_caption = f"📄 *Official PDF Document Attached*\n{art.get('title')[:100]}"
                print(f"📎 Attaching official PDF file: {art['url']}...")
                doc_ok, doc_res = dispatcher.send_document(art["url"], caption=pdf_caption)
                print(f"📎 PDF Attachment Status: {doc_ok} ({doc_res})")

            log_dispatch(
                channel=channel_name,
                recipient=str(recipient),
                article_count=1,
                status="SUCCESS" if success else "FAILED",
                response_preview=response_text
            )
            if success:
                dispatched_count += 1
            # Brief pause to respect Telegram rate limits
            time.sleep(2.0)

        return {
            "new_scraped": len(new_articles),
            "dispatched": dispatched_count,
            "status": "SUCCESS" if dispatched_count > 0 else "FAILED",
            "response": last_resp
        }


def run_continuous_loop():
    """Run continuously in the background at configured intervals."""
    print("==================================================")
    print("🎓 Mera Exam Bot - Realtime Exam Alert Service")
    print("==================================================")
    init_db()

    while True:
        try:
            config = load_config()
            interval_mins = max(5, config.get("polling_interval_minutes", 30))
            
            run_pipeline_once(config)

            print(f"⏳ Sleeping for {interval_mins} minutes until next scan. Press Ctrl+C to stop.\n")
            time.sleep(interval_mins * 60)
        except KeyboardInterrupt:
            print("\n🛑 Service stopped by user.")
            break
        except Exception as e:
            print(f"[Loop Exception] {e}")
            time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mera Exam Bot News Service")
    parser.add_argument("--once", action="store_true", help="Run scan once and exit")
    parser.add_argument("--test", action="store_true", help="Send a test message to Telegram/WhatsApp")
    args = parser.parse_args()

    cfg = load_config()

    if args.test:
        disp = get_dispatcher(cfg)
        print(f"Testing alert connection using '{cfg.get('whatsapp_provider')}' provider...")
        ok, res = disp.test_connection()
        print(f"Result: {'SUCCESS' if ok else 'FAILED'}")
        print(f"Details: {res}")
        sys.exit(0 if ok else 1)
    elif args.once:
        run_pipeline_once(cfg)
    else:
        run_continuous_loop()
