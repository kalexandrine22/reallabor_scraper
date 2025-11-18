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

RESULTS_FILEPATH = "results/bing_news_results.json"


def fetch_bing_rss(query: str) -> list:
    """
    Fetches RSS entries for a single query from Bing News.
    """
    encoded_query = quote(query)
    rss_url = (
        f"https://www.bing.com/news/search?q={encoded_query}&format=rss"
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

    results = []
    for entry in feed.entries:
        # Bing packs the source in entry.source.title
        source_title = None
        if hasattr(entry, "source") and hasattr(entry.source, "title"):
            source_title = entry.source.title

        results.append(
            {
                "query": query,
                "title": entry.title,
                "source": source_title,
                "published": entry.get("published", None),
                "link": entry.link,
            }
        )

    return results


def get_bing_news_results(queries: list) -> None:
    """
    Collects article results from Bing RSS queries.
    Uses Playwright to extract the true publisher URL.
    Saves results to a JSON file.
    """
    all_results = []
    start_time = time.time()

    print("\n📰 Starte Bing News RSS-Abfragen...\n")

    for query in tqdm(queries, desc="Fortschritt", ncols=90, colour="cyan"):
        all_results.extend(fetch_bing_rss(query))

    elapsed = time.time() - start_time
    print(f"🕒 Laufzeit: {elapsed:.1f} Sekunden\n")

    print("\n📰Artikel-URLs sammeln...\n")
    start_time = time.time()

    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            page = browser.new_page()

            for result in tqdm(
                all_results,
                desc="Fortschritt",
                ncols=90,
                colour="green",
            ):
                try:
                    page.goto(result["link"], timeout=20000)

                    # Bing hat keine Cookie-Abfrage wie Google, aber falls doch:
                    try:
                        page.get_by_role("button", name="Alle ablehnen").click()
                    except Exception:
                        pass

                    result["article_url"] = page.url
                    result["publication"] = urlparse(page.url).hostname

                except Exception as e:
                    result["article_url"] = None
                    result["publication"] = None

    elapsed = time.time() - start_time
    print(f"🕒 Laufzeit: {elapsed:.1f} Sekunden\n")

    with open(RESULTS_FILEPATH, "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(
        f"\n✅ Fertig! {len(all_results)} Artikel gespeichert in {RESULTS_FILEPATH}"
    )
