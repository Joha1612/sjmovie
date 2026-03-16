import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import json
import re

# BASE = "https://fibwatch.art/videos/latest"
BASE = "https://mlsbd.co"


session = cloudscraper.create_scraper()


def get_watch_links(url):

    r = session.get(url)
    soup = BeautifulSoup(r.text, "lxml")

    links = set()

    for a in soup.find_all("a", href=True):

        full = urljoin(url, a["href"])

        if "/watch/" in full and full.endswith(".html"):
            links.add(full)

    return list(links)


def extract_quality(url):

    q = re.search(r"(480p|720p|1080p|2160p)", url, re.I)

    if q:
        return q.group(1).lower()

    return "unknown"


def unwrap_shortlink(link):

    if "url=" in link:

        parsed = urlparse(link)
        qs = parse_qs(parsed.query)

        real = qs.get("url")

        if real:
            return real[0]

    return link


def scrape_watch_page(url):

    r = session.get(url)

    soup = BeautifulSoup(r.text, "lxml")

    # title
    title = soup.find("title")

    name = title.text.split("-")[0].strip() if title else "Unknown"

    # poster
    poster = None

    meta = soup.find("meta", property="og:image")

    if meta:
        poster = meta.get("content")

    # watch player
    watch = None

    iframe = soup.find("iframe")

    if iframe:
        watch = urljoin(url, iframe.get("src"))

    downloads = []
    seen = set()

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if ".mkv" in href or ".mp4" in href:

            link = unwrap_shortlink(urljoin(url, href))

            if link in seen:
                continue

            seen.add(link)

            quality = extract_quality(link)

            downloads.append({

                "quality": quality,
                "download": link,
                "watch": watch

            })

    return {

        "name": name,
        "poster": poster,
        "qualities": downloads
    }


all_movies = []

for page in range(1, 4):

    url = BASE if page == 1 else f"{BASE}?page_id={page}"

    watch_links = get_watch_links(url)

    for link in watch_links:

        movie = scrape_watch_page(link)

        if movie["qualities"]:
            all_movies.append(movie)


with open("movies.json", "w", encoding="utf-8") as f:

    json.dump(all_movies, f, indent=4, ensure_ascii=False)

print("Saved", len(all_movies), "movies")