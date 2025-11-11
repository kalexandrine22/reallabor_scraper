from urllib.parse import quote

import requests
import feedparser


def fetch_google_rss(query):
    """Fetches RSS entries for a single query from Google News."""
    encoded_query = quote(query)
    rss_url = (
        f"https://news.google.com/rss/search?q={encoded_query}"
        "&hl=de&gl=DE&ceid=DE:de"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0 Safari/537.36"
        ),
        "Accept-Language": "de-DE,de;q=0.9"
    }

    response = requests.get(rss_url, headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"⚠️ Fehler bei {query}: HTTP {response.status_code}")
        return []

    feed = feedparser.parse(response.text)
    return [
        {
            "query": query,
            "title": entry.title,
            "source": entry.get("source", {}).get("title")
            if "source" in entry else None,
            "published": entry.get("published", None),
            "link": entry.link
        }
        for entry in feed.entries
    ]