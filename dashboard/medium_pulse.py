#!/usr/bin/env python3
"""
Medium Pulse — fetch latest AI articles from Medium RSS feeds.
Feeds the AI Pulse section of the AI Dashboard.
"""

import json
import urllib.parse
import urllib.request
import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from langdetect import detect, LangDetectException
from langcodes import Language
from deep_translator import GoogleTranslator

CACHE_FILE = Path(__file__).parent.parent / "data" / "url_cache.json"


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict) -> None:
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def shorten_url(url: str, cache: dict) -> str:
    base = url.split("?")[0]
    if base in cache:
        return cache[base]
    try:
        api = f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(base, safe=':/@')}"
        with urllib.request.urlopen(api, timeout=5) as r:
            short = r.read().decode().strip()
        cache[base] = short
        return short
    except Exception:
        return url

FEEDS = {
    "Artificial Intelligence": "https://medium.com/feed/tag/artificial-intelligence",
    "LLM": "https://medium.com/feed/tag/llm",
    "AI Agents": "https://medium.com/feed/tag/ai-agents",
    "Generative AI": "https://medium.com/feed/tag/generative-ai",
    "Towards Data Science": "https://medium.com/feed/towards-data-science",
}

MAX_PER_FEED = 3


def detect_language(text: str) -> tuple[str, str]:
    """Returns (language_name_in_english, language_code)."""
    try:
        code = detect(text)
        name = Language.get(code).display_name("en")
        return name, code
    except LangDetectException:
        return "Unknown", "en"


def translate_title(title: str, lang_code: str) -> str:
    try:
        return GoogleTranslator(source=lang_code, target="en").translate(title)
    except Exception:
        return title


def parse_date(entry) -> datetime:
    for field in ("published", "updated"):
        raw = entry.get(field)
        if raw:
            try:
                return parsedate_to_datetime(raw)
            except Exception:
                pass
    return datetime.min.replace(tzinfo=timezone.utc)


def fetch_articles() -> list[dict]:
    cache = _load_cache()
    articles = []
    seen_ids = set()
    for label, url in FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:MAX_PER_FEED]:
            link = entry.get("link", "")
            # Medium uses different paths for the same article across tags;
            # the hex ID at the end of the slug is always unique per article.
            article_id = link.split("?")[0].rstrip("/").split("-")[-1]
            if article_id in seen_ids:
                continue
            seen_ids.add(article_id)

            title = entry.get("title", "No title")
            lang_name, lang_code = detect_language(title)
            is_english = lang_code.startswith("en")
            translated = None if is_english else translate_title(title, lang_code)
            short_url = shorten_url(link, cache)

            articles.append({
                "source": label,
                "title": title,
                "translated_title": translated,
                "author": entry.get("author", "Unknown"),
                "url": short_url,
                "date": parse_date(entry),
                "language": lang_name,
                "is_english": is_english,
            })
    _save_cache(cache)
    return sorted(articles, key=lambda a: a["date"], reverse=True)
