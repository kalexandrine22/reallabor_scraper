# reallabor_news_scraper.py
# -------------------------------------------------
# Robust Bing News RSS Scraper for "Reallabor" + City
# Author: Kendra Alexander
# -------------------------------------------------

import requests
import feedparser
import pandas as pd
from tqdm import tqdm
from urllib.parse import quote
import time


def fetch_bing_rss(query):
    """Fetches RSS entries for a single query from Bing News."""
    encoded_query = quote(query)
    rss_url = (
        f"https://www.bing.com/news/search?q={encoded_query}"
        "&format=rss&setLang=de-DE&setmkt=de-DE"
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


def main():
    queries = [
        '"Reallabor" Wuppertal',
        '"Reallabor" Karlsruhe',
        '"Reallabor" Lüneburg',
        '"Reallabor" Berlin',
        '"Reallabor" Stuttgart',
        '"Reallabor" Dresden'
    ]

    all_results = []
    start_time = time.time()

    print("\n📰 Starte Bing-RSS-Abfragen...\n")
    for query in tqdm(queries, desc="Fortschritt", ncols=90, colour="cyan"):
        results = fetch_bing_rss(query)
        all_results.extend(results)
        time.sleep(0.5)  # kleine Pause, um freundlich zu bleiben

    df = pd.DataFrame(all_results)
    df.to_csv("reallabor_news.csv", index=False, encoding="utf-8-sig")

    elapsed = time.time() - start_time
    print(f"\n✅ Fertig! {len(df)} Artikel gespeichert in reallabor_news.csv")
    print(f"🕒 Laufzeit: {elapsed:.1f} Sekunden\n")


if __name__ == "__main__":
    main()
