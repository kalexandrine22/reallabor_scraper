# 📰 Reallabor News Scraper

Dieses Projekt durchsucht **Google News** automatisch nach Artikeln, die den Begriff **„Reallabor“** in Verbindung mit deutschen Städten enthalten (z. B. Wuppertal, Karlsruhe, Berlin, Stuttgart, Dresden, Lüneburg).  
Die Ergebnisse werden als CSV-Datei gespeichert und können anschließend für weitere Textanalysen oder qualitative Forschung verwendet werden.

---

## 🚀 Funktionen

- Automatisierte Suche in Google News (über `gnews`-Modul)
- Unterstützung mehrerer Städte und Suchbegriffe
- Speicherung aller Ergebnisse als CSV-Datei (`reallabor_news.csv`)
- Optionale Erweiterung: Herunterladen der Artikeltexte (lokale Speicherung)
- Leicht konfigurierbar für eigene Begriffe oder Regionen

---

## 🧰 Setup

### Voraussetzungen

- macOS oder Linux (Python 3.10+ empfohlen)
- Git & Virtual Environment (`venv`)
- Internetverbindung

### Installation

```sh
# clone repository
git clone https://github.com/kalexandrine22/reallabor_scraper.git

# create virtual environment and activate it
python3 -m venv .venv
. .venv/bin/activate

# install packages
pip install -r _requirements.txt
```
