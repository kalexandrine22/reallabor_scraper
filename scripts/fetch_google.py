import time
import json
from urllib.parse import quote, urlparse

from tqdm import tqdm
from playwright.sync_api import sync_playwright
import requests
import feedparser

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/118.0 Safari/537.36"
)

RESULTS_FILEPATH = "results/google_news_results.json"


def fetch_google_rss(query: str) -> list:
    """
    Fetches RSS entries for a single query from Google News.
    """
    encoded_query = quote(query)
    rss_url = (
        f"https://news.google.com/rss/search?q={encoded_query}&hl=de&gl=DE&ceid=DE:de"
    )

    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "de-DE,de;q=0.9",
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
            if "source" in entry
            else None,
            "published": entry.get("published", None),
            "link": entry.link,
        }
        for entry in feed.entries
    ]


def get_google_news_results(queries: list) -> None:
    """
    Collects article results from RSS queries
    After RSS feed results are collected, uses playwright to find
    article publishers and urls

    Saves results to json file
    """
    all_results = []
    start_time = time.time()

    print("\n📰 Starte Google News RSS-Abfragen...\n")

    for query in tqdm(queries, desc="Fortschritt", ncols=90, colour="cyan"):
        all_results.extend(fetch_google_rss(query))

    elapsed = time.time() - start_time

    print(f"🕒 Laufzeit: {elapsed:.1f} Sekunden\n")

    start_time = time.time()

    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            page = browser.new_page()

            print("\n📰Artikel-URLs sammeln...\n")

            for result in tqdm(
                all_results,
                desc="Fortschritt",
                ncols=90,
                colour="green",
            ):
                page.goto(result["link"])

                # navigate past Google's cookie page if it's encountered
                try:
                    page.get_by_role("button", name="Alle ablehnen").click()
                # button not found, continue
                except Exception:
                    pass

                # save the true article url and publisher host to the result
                result["article_url"] = page.url
                result["publication"] = urlparse(page.url).hostname

    elapsed = time.time() - start_time
    print(f"🕒 Laufzeit: {elapsed:.1f} Sekunden\n")

    with open(RESULTS_FILEPATH, "w") as f:
        json.dump(all_results, f, indent=2)

    print(
        f"\n✅ Fertig! {len(all_results)} Artikel gespeichert in results/google_news_results.json"
    )
