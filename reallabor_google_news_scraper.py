# reallabor_google_news_scraper.py
# -------------------------------------------------
# Google News RSS Scraper for "Reallabor" + City
# Author: Kendra Alexander
# -------------------------------------------------

import time 

import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

from fetch import fetch_google_rss

QUERIES = [
        '"Reallabor" Wuppertal',
        '"Reallabor" Karlsruhe',
        '"Reallabor" Lüneburg',
        '"Reallabor" Berlin',
        '"Reallabor" Stuttgart',
        '"Reallabor" Dresden',
        '"Reallabor" Nachhaltigkeit'
    ]

def main():
    all_results = []
    start_time = time.time()

    print("\n📰 Starte Google News RSS-Abfragen...\n")
    for query in tqdm(QUERIES, desc="Fortschritt", ncols=90, colour="cyan"):
        results = fetch_google_rss(query)
        all_results.extend(results)
        time.sleep(0.5)

    for result in all_results:
        print(result)
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, )
            page = browser.new_page()
            page.goto(result["link"])
            
            if locator := page.get_by_role("button", name="Alle ablehnen"):
                locator.click()
                

            time.sleep(5)
            
            # print(page.title())
            # browser.close()
        break

    df = pd.DataFrame(all_results)
    df.to_csv("reallabor_google_news.csv", index=False, encoding="utf-8-sig")

    elapsed = time.time() - start_time
    print(f"\n✅ Fertig! {len(df)} Artikel gespeichert in reallabor_google_news.csv")
    print(f"🕒 Laufzeit: {elapsed:.1f} Sekunden\n")


if __name__ == "__main__":
    main()
    
