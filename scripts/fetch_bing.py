import time
import os
import json
from urllib.parse import quote, urlparse

from tqdm import tqdm
from playwright.sync_api import sync_playwright
import requests
import feedparser


# -------------------------------------------------------
# Pfade korrekt absolut bauen
# -------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
RESULTS_FILEPATH = os.path.join(RESULTS_DIR, "bing_news_results.json")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/118.0 Safari/537.36"
)


# -------------------------------------------------------
# RSS-Abfrage von Bing
# -------------------------------------------------------
def fetch_bing_rss(query: str) -> list:
    """
    Fetches RSS entries for a single query from Bing News.
    """
    encoded_query = quote(query)
    rss_url = f"https://www.bing.com/news/search?q={encoded_query}&format=rss"

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


# -------------------------------------------------------
# Hauptfunktion: Bing-Ergebnisse + Playwright für echte URLs
# -------------------------------------------------------
def get_bing_news_results(queries: list) -> None:
    """
    Collects article results from Bing RSS queries.
    Uses Playwright to extract the true publisher URL.
    Saves results to a JSON file.
    """

    # Ordner erstellen, falls er fehlt
    os.makedirs(RESULTS_DIR, exist_ok=True)

    all_results = []

    print("\n📰 Starte Bing News RSS-Abfragen...\n")
    start_time = time.time()

    # RSS-Daten sammeln
    for query in tqdm(queries, desc="Fortschritt RSS", ncols=90, colour="cyan"):
        all_results.extend(fetch_bing_rss(query))

    print(f"🕒 RSS-Abfragen Laufzeit: {time.time() - start_time:.1f} Sekunden\n")

    # Playwright zum Auflösen der echten URLs
    print("🔍 Sammle tatsächliche Artikel-URLs...\n")
    start_time = time.time()

    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            page = browser.new_page()

            for result in tqdm(
                all_results,
                desc="Fortschritt URLs",
                ncols=90,
                colour="green",
            ):
                try:
                    page.goto(result["link"], timeout=20000)

                    # falls Cookie Banner
                    try:
                        page.get_by_role("button", name="Alle ablehnen").click()
                    except Exception:
                        pass

                    result["article_url"] = page.url
                    result["publication"] = urlparse(page.url).hostname

                except Exception:
                    result["article_url"] = None
                    result["publication"] = None

    print(f"🕒 URL-Auflösung Laufzeit: {time.time() - start_time:.1f} Sekunden\n")

    # JSON speichern
    with open(RESULTS_FILEPATH, "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"✅ Fertig! {len(all_results)} Artikel gespeichert in: {RESULTS_FILEPATH}")


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
def main():
    queries = [
        '"Reallabor" Wuppertal',
        '"Reallabor" Karlsruhe',
        '"Reallabor" Lüneburg',
        '"Reallabor" Berlin',
        '"Reallabor" Stuttgart',
        '"Reallabor" Dresden',
        '"Reallabor" Nachhaltigkeit'
    ]

    get_bing_news_results(queries)


if __name__ == "__main__":
    main()
