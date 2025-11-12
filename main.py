"""
Google News RSS Scraper for "Reallabor" + City
Authors: Kendra Alexander, Robert Adams
"""

import json
import yaml
import posixpath

from dotenv import dotenv_values
from tqdm import tqdm
import trafilatura

from scripts.fetch import get_google_news_results
from scripts.sceibo import Sciebo

CONFIG = dotenv_values(".env")
SCIEBO_COLLECTION = "reallabor"
SCEIBO_DIRECTORY = "google_news"
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

    # create the sceibo collection if not exists
    Sciebo.mkcol(
        token=CONFIG["SCIEBO_TOKEN"],
        password=CONFIG["SCIEBO_PASSWORD"],
        webdav_url=CONFIG["WEBDAV_URL"],
        dest=SCIEBO_COLLECTION,
    )
    DEST = f"{SCIEBO_COLLECTION}/{SCEIBO_DIRECTORY}"
    Sciebo.mkcol(
        token=CONFIG["SCIEBO_TOKEN"],
        password=CONFIG["SCIEBO_PASSWORD"],
        webdav_url=CONFIG["WEBDAV_URL"],
        dest=DEST,
    )

    # if we can't scrape some articles, save them for later manual parsing
    google_news_results_not_scraped = []

    for result in tqdm(google_results):
        """
        There are 89 unique publications, it's too much to write a scraper for each of them
        Here might be a good spot to use trafilatura using the real url
        """
        article_url = result["article_url"]

        if downloaded := trafilatura.fetch_url(article_url):
            # specifying with_metadata will give us some extra article info like date, sitename, etc.
            content = trafilatura.extract(downloaded, with_metadata=True)
            if content is not None and content.startswith("---"):
                try:
                    # separate out the metadata so we can use it in filenames
                    _, metadata, _ = content.split("---", 2)
                    metadata = yaml.safe_load(metadata)  # convert metadata to dict
                    filename = f"{metadata['date']} {metadata['title']}.txt"
                    filepath = posixpath.join(DEST, filename)
                    Sciebo.upload(
                        token=CONFIG["SCIEBO_TOKEN"],
                        password=CONFIG["SCIEBO_PASSWORD"],
                        webdav_url=CONFIG["WEBDAV_URL"],
                        filepath=filepath,
                        content=content,
                    )
                except Exception:
                    google_news_results_not_scraped.append(result)
            else:
                google_news_results_not_scraped.append(result)

        if len(google_news_results_not_scraped) > 0:
            with open("results/google_news_results_not_scraped.json", "w") as f:
                json.dump(google_news_results_not_scraped, f, indent=2)

        # remove this break to loop over all results
        break


if __name__ == "__main__":
    main()
