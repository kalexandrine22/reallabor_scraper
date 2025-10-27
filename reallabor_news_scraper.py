# reallabor_news_scraper.py
# ---------------------------------
# Fetches Google News RSS feeds for "Reallabor" + city
# Author: Kendra Alexander
# ---------------------------------

import feedparser
import pandas as pd
from tqdm import tqdm
from urllib.parse import quote

def fetch_bing_news(queries):
    all_results = []
    print("\n📰 Starte Bing News RSS-Suche...\n")
    for query in tqdm(queries, desc="RSS Feeds", ncols=90, colour="cyan"):
        encoded_query = quote(query)
        rss_url = f"https://www.bing.com/news/search?q={encoded_query}&format=rss"
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            all_results.append({
                "query": query,
                "title": entry.title,
                "source": entry.source.title if "source" in entry else None,
                "published": entry.published if "published" in entry else None,
                "link": entry.link
            })
    return pd.DataFrame(all_results)


def main():
    queries = [
        '"Reallabor" Wuppertal',
        '"Reallabor" Karlsruhe',
        '"Reallabor" Lüneburg',
        '"Reallabor" Berlin',
        '"Reallabor" Stuttgart',
        '"Reallabor" Dresden'
    ]

    df = fetch_bing_news(queries)
    df.to_csv("reallabor_news.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ Suche abgeschlossen — {len(df)} Artikel gespeichert!\n")


if __name__ == "__main__":
    main()
