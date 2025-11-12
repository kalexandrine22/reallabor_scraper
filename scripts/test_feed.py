import requests
import feedparser
from urllib.parse import quote

# --- Testabfrage ---
query = '"Reallabor" Wuppertal'
encoded_query = quote(query)
rss_url = (
    f"https://www.bing.com/news/search?q={encoded_query}"
    "&format=rss&setLang=de-DE&setmkt=de-DE"
)

print(f"🔍 Teste RSS-Feed:\n{rss_url}\n")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/118.0 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9"
}

response = requests.get(rss_url, headers=headers, timeout=10)
print(f"🌐 HTTP-Status: {response.status_code}")
print(f"Antwort-Länge: {len(response.text)} Zeichen\n")

# Prüfen, ob überhaupt Items im Text vorkommen
if "<item>" not in response.text:
    print("⚠️ Keine <item>-Einträge erkannt — mögliche Lokalisierung oder Sprachproblem.")
    print(response.text[:500])
else:
    feed = feedparser.parse(response.text)
    print(f"✅ {len(feed.entries)} Artikel gefunden.\n")

    for i, entry in enumerate(feed.entries[:5], start=1):
        print(f"{i}. {entry.title}")
        print(f"   Quelle: {entry.get('source', {}).get('title') if 'source' in entry else 'Unbekannt'}")
        print(f"   Datum: {entry.get('published', 'n/a')}")
        print(f"   Link:  {entry.link}\n")
