"""
Google News RSS Scraper for "Reallabor" + City
Authors: Kendra Alexander, Robert Adams
"""

import json

from scripts.fetch import get_google_news_results

RESULTS_FILEPATH = "results/google_news_results.json"

QUERIES = [
    '"Reallabor" Wuppertal',
    '"Reallabor" Karlsruhe',
    '"Reallabor" Lüneburg',
    '"Reallabor" Berlin',
    '"Reallabor" Stuttgart',
    '"Reallabor" Dresden',
    '"Reallabor" Nachhaltigkeit',
]


def main():
    try:
        with open(RESULTS_FILEPATH) as f:
            google_results: list = json.load(f)
    except FileNotFoundError:
        google_results = get_google_news_results(QUERIES)

    for result in google_results:
        """
        There are 89 unique publications, it's too much to write a scraper for each of them
        Here might be a good spot to use trafilatura using the real url
        """
        article_url = result["article_url"]


if __name__ == "__main__":
    main()
