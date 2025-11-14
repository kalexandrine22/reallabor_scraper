import os
import json
import trafilatura
from tqdm import tqdm
from urllib.parse import urlparse
from dotenv import load_dotenv
from sciebo import Sciebo

# === LOAD ENVIRONMENT VARIABLES ===
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

WEBDAV_URL = os.getenv("WEBDAV_URL")
TOKEN = os.getenv("SCIEBO_TOKEN")
PASSWORD = os.getenv("SCIEBO_PASSWORD")
SCIEBO_FOLDER = os.getenv("SCIEBO_FOLDER", "Reallabor_Articles")
RESULTS_FILE = os.getenv("RESULTS_FILE", "results/google_news_results.json")

# Local backup folder
LOCAL_SAVE_DIR = os.path.join("results", "articles_txt_full")


def fetch_and_upload_articles():
    """Extracts article text from JSON metadata and uploads to Sciebo."""

    # Load results JSON
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)

    os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)
    Sciebo.mkcol(WEBDAV_URL, SCIEBO_FOLDER, TOKEN, PASSWORD)

    for idx, article in tqdm(enumerate(articles, start=1), total=len(articles), desc="Processing"):
        title = article.get("title", "Untitled")
        source = article.get("source", "")
        published = article.get("published", "")
        query = article.get("query", "")
        google_url = article.get("link", "")
        real_url = article.get("article_url", "")

        # Fetch article text
        downloaded = trafilatura.fetch_url(real_url)
        content = trafilatura.extract(downloaded, include_comments=False, include_images=False)
        if not content:
            content = "(Could not extract article text — may be paywalled or blocked.)"

        # Build readable text content
        text_content = f"""TITLE: {title}
SOURCE: {source}
PUBLISHED: {published}
QUERY: {query}
GOOGLE URL: {google_url}
REAL URL: {real_url}

ARTICLE CONTENT:
{content}
"""

        # Safe filenames
        safe_host = urlparse(real_url).hostname or "unknown"
        safe_title = "".join(c for c in title[:60] if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_")
        local_filename = f"{safe_host}_{idx}.txt"
        local_path = os.path.join(LOCAL_SAVE_DIR, local_filename)
        remote_path = f"{SCIEBO_FOLDER}/{local_filename}"

        # Save local backup
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(text_content)

        # Upload to Sciebo
        Sciebo.upload(WEBDAV_URL, remote_path, text_content, TOKEN, PASSWORD)

    print(f"\n✅ All {len(articles)} articles processed and uploaded to Sciebo.")
    print(f"🗂️ Local backups saved in: {LOCAL_SAVE_DIR}")


if __name__ == "__main__":
    #print(WEBDAV_URL + SCIEBO_FOLDER) moin
    fetch_and_upload_articles()
