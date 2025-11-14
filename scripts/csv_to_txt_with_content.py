import os #Create folders, join file paths safely
import pandas as pd #Read the CSV that contains your article metadata
import requests #Follow Google redirect links to real article URLs
import trafilatura #Extract readable article text from web pages
from tqdm import tqdm #Display progress bars in the terminal
from urllib.parse import urlparse #Helps with URL handling (not actually used in this snippet)

def get_real_url(google_url):
    """Follow the redirect from Google News RSS to the real article URL."""
    try:
        # Allow redirects and use a browser-like header
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(google_url, headers=headers, allow_redirects=True, timeout=10)
        return response.url  # final destination after redirect
    except Exception:
        return google_url

def export_articles_with_text(csv_path, folder="articles_txt_full"):
    """Fetch full article text and save as .txt files."""
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    os.makedirs(folder, exist_ok=True)

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Downloading articles"):
        safe_query = row["query"].replace('"', '').replace(' ', '_')
        filename = f"{safe_query}_{idx+1}.txt"
        filepath = os.path.join(folder, filename)

        google_url = row.get("link", "")
        real_url = get_real_url(google_url)

        # Fetch and extract main article text
        downloaded = trafilatura.fetch_url(real_url)
        content = trafilatura.extract(downloaded, include_comments=False, include_images=False)

        if not content:
            content = "(Could not extract article text — may be paywalled or blocked.)"

        content_lines = [
            f"TITLE: {row.get('title', '')}",
            f"SOURCE: {row.get('source', '')}",
            f"PUBLISHED: {row.get('published', '')}",
            f"GOOGLE URL: {google_url}",
            f"REAL URL: {real_url}",
            "",
            "ARTICLE CONTENT:",
            content
        ]

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(content_lines))

    print(f"\n✅ Exported {len(df)} articles (with full text when available).")

if __name__ == "__main__":
    import sys

    # If user provides a filename (e.g. python script.py myfile.csv)
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = "reallabor_google_news.csv"  # default fallback

    export_articles_with_text(csv_path)
