# csv_to_txt.py
# -------------------------------------------------
# Convert scraped CSV (e.g., from Google News) into text files
# Author: Kendra Alexander
# -------------------------------------------------

import os
import pandas as pd


def export_articles_to_txt(csv_path, folder="articles_txt"):
    """Read the CSV of articles and write one .txt file per article."""
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    os.makedirs(folder, exist_ok=True)

    for idx, row in df.iterrows():
        # Create a safe filename: query + index number
        safe_query = row["query"].replace('"', '').replace(' ', '_')
        filename = f"{safe_query}_{idx+1}.txt"
        filepath = os.path.join(folder, filename)

        # Build text content
        content_lines = [
            f"TITLE: {row.get('title', '')}",
            f"SOURCE: {row.get('source', '')}",
            f"PUBLISHED: {row.get('published', '')}",
            f"URL: {row.get('link', '')}",
            "",
            "ARTICLE CONTENT:",
            "(no content yet — metadata only)"
        ]

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(content_lines))

    print(f"✅ Exported {len(df)} articles to folder: {folder}")


if __name__ == "__main__":
    export_articles_to_txt("reallabor_google_news.csv")
