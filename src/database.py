import hashlib
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DB_DIR / "news_alerts.db"


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Ensure directory exists and yield SQLite connection with row_factory, safely closing on exit."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize database tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                exam_category TEXT NOT NULL,
                priority TEXT DEFAULT 'MEDIUM',
                published_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_sent INTEGER DEFAULT 0,
                sent_at TIMESTAMP,
                delivery_status TEXT DEFAULT 'PENDING',
                error_message TEXT
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_hash ON articles(content_hash);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_is_sent ON articles(is_sent);
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dispatch_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel TEXT NOT NULL,
                recipient TEXT NOT NULL,
                article_count INTEGER DEFAULT 1,
                status TEXT NOT NULL,
                response_preview TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def compute_hash(title: str, url: str) -> str:
    """Compute SHA-256 fingerprint for title + url deduplication."""
    norm_title = "".join(title.lower().split())
    norm_url = url.split("?")[0].strip()
    return hashlib.sha256(f"{norm_title}|{norm_url}".encode("utf-8")).hexdigest()


def is_article_seen(content_hash: str) -> bool:
    """Check if an article hash is already stored."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM articles WHERE content_hash = ? LIMIT 1", (content_hash,))
        return cursor.fetchone() is not None


def save_article(article: Dict[str, Any]) -> Optional[int]:
    """Save article if not exists. Returns article ID or None if duplicate."""
    h = article.get("content_hash") or compute_hash(article["title"], article["url"])
    if is_article_seen(h):
        return None

    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO articles (
                    content_hash, title, url, source, exam_category, priority, published_date, is_sent, delivery_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'PENDING')
            """, (
                h,
                article["title"],
                article["url"],
                article.get("source", "Unknown"),
                article.get("exam_category", "GENERAL"),
                article.get("priority", "MEDIUM"),
                article.get("published_date", datetime.now().isoformat())
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None


def get_unsent_articles(limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch pending unsent articles, prioritizing high priority."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM articles 
            WHERE is_sent = 0 
            ORDER BY 
                CASE priority 
                    WHEN 'HIGH' THEN 1 
                    WHEN 'MEDIUM' THEN 2 
                    ELSE 3 
                END, 
                id DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]


def mark_article_sent(article_id: int, status: str = "SENT", error_message: Optional[str] = None):
    """Update article delivery status."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        is_sent_flag = 1 if status in ("SENT", "DRY_RUN") else 0
        cursor.execute("""
            UPDATE articles 
            SET is_sent = ?, sent_at = CURRENT_TIMESTAMP, delivery_status = ?, error_message = ?
            WHERE id = ?
        """, (is_sent_flag, status, error_message, article_id))
        conn.commit()


def get_recent_articles(limit: int = 50, exam_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve recent articles for dashboard view."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if exam_filter and exam_filter.upper() != "ALL":
            cursor.execute("""
                SELECT * FROM articles 
                WHERE exam_category = ?
                ORDER BY id DESC LIMIT ?
            """, (exam_filter.upper(), limit))
        else:
            cursor.execute("SELECT * FROM articles ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]


def get_stats() -> Dict[str, Any]:
    """Return summary statistics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM articles WHERE is_sent = 1")
        sent = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM articles WHERE is_sent = 0")
        pending = cursor.fetchone()[0]

        cursor.execute("SELECT created_at FROM articles ORDER BY id DESC LIMIT 1")
        last_row = cursor.fetchone()
        last_article_time = last_row[0] if last_row else None

        cursor.execute("SELECT created_at FROM dispatch_logs ORDER BY id DESC LIMIT 1")
        last_dispatch_row = cursor.fetchone()
        last_dispatch_time = last_dispatch_row[0] if last_dispatch_row else None

        # Breakdown by exam
        cursor.execute("SELECT exam_category, COUNT(*) FROM articles GROUP BY exam_category")
        exam_counts = {row[0]: row[1] for row in cursor.fetchall()}

        return {
            "total_articles": total,
            "sent_alerts": sent,
            "pending_alerts": pending,
            "last_article_time": last_article_time,
            "last_dispatch_time": last_dispatch_time,
            "exam_counts": exam_counts
        }


def log_dispatch(channel: str, recipient: str, article_count: int, status: str, response_preview: str = ""):
    """Record dispatch event in log."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dispatch_logs (channel, recipient, article_count, status, response_preview)
            VALUES (?, ?, ?, ?, ?)
        """, (channel, recipient, article_count, status, response_preview[:250]))
        conn.commit()


# Automatically initialize DB on import
init_db()
