import json
import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time

# ---------- SESSION ----------
session = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

DATABASE_FILE = "database.json"

START_PAGE = 1
END_PAGE = 2
MOVIE_THREADS = 8

VIDEO_FORMATS = (".mkv", ".mp4", ".avi", ".mov", ".webm")

# 🔥 CDN PRIORITY
PRIORITY_CDN = ["atryh78", "b-cdn.net"]

CATEGORIES = {
    "Bangla & Kolkata": "https://fibwatch.art/videos/category/1",
    "Web Series": "https://fibwatch.art/videos/category/3",
    "Hindi": "https://fibwatch.art/videos/category/4",
    "Hindi Dubbed": "https://fibwatch.art/videos/category/5",
    "Bangla Dubbed": "https://fibwatch.art/videos/category/852",
    "Natok": "https://fibwatch.art/videos/category/855",
}

# ---------- DATABASE ----------
def load_database():
    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_database(data):
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------- REQUEST ----------
def safe_request(url, retries=4):
    for _ in range(retries):
        try:
            r = session.get(url, timeout=20)
            if r.status_code == 200:
                return r
        except:
            pass
        time.sleep(2)
    return None

# ---------- DEAD LINK CHECK ----------
def is_working(url):
    try:
        r = requests.head(url, timeout=5)
        return r.status_code < 400
    except:
        return False

# ---------- GET WATCH LINKS ----------
def get_watch_links(base_url):
    links = []

    for page in range(START_PAGE, END_PAGE + 1):
        url = f"{base_url}?page_id={page}"
        print("Scanning:", url)

        r = safe_request(url)
        if not r:
            continue

        soup = BeautifulSoup(r.text, "lxml")

        for a in soup.select("a[href*='/watch/']"):
            link = urljoin(url, a["href"])
            link = link.split("?")[0].rstrip("/")

            if link not in links:
                links.append(link)

    print("Total watch pages:", len(links))
    return links

# ---------- EXTRACT DOWNLOADS (PRO) ----------
def extract_downloads(soup):

    priority = {}
    fallback = {}

    for a in soup.find_all("a", href=True):

        href = a["href"].strip()
        lower = href.lower()

        if any(ext in lower for ext in VIDEO_FORMATS):

            if "urlshortlink" in lower:
                continue

            filename = href.split("/")[-1].lower()

            # PRIORITY CDN
            if "atryh78" in lower:
                priority[filename] = href

            # FALLBACK CDN
            elif "b-cdn.net" in lower:
                if filename not in priority:
                    fallback[filename] = href

    # ---------- MERGE ----------
    final_links = {}

    for fname in set(list(priority.keys()) + list(fallback.keys())):

        link = priority.get(fname) or fallback.get(fname)

        # 🔥 DEAD LINK CHECK
        if link and is_working(link):
            final_links[fname] = link

    return list(final_links.values())

# ---------- SCRAPE MOVIE ----------
def scrape_movie(url):

    time.sleep(0.5)

    r = safe_request(url)
    if not r:
        return None

    soup = BeautifulSoup(r.text, "lxml")

    title = soup.find("title")
    if not title:
        return None

    name = title.text.split("-")[0].strip()

    poster = None
    meta = soup.find("meta", property="og:image")
    if meta:
        poster = meta.get("content")

    downloads = extract_downloads(soup)

    return {
        "name": name,
        "poster": poster,
        "downloads": downloads,
        "url": url
    }

# ---------- MAIN ----------
def run_scraper():

    database = load_database()

    movie_index = {m["name"].lower().strip(): m for m in database}

    new_movies = []

    for category, url in CATEGORIES.items():

        print("\nCategory:", category)

        watch_links = get_watch_links(url)

        with ThreadPoolExecutor(max_workers=MOVIE_THREADS) as executor:

            futures = [executor.submit(scrape_movie, link) for link in watch_links]

            for future in as_completed(futures):

                movie = future.result()
                if not movie or not movie["downloads"]:
                    continue

                movie["category"] = category

                key = movie["name"].lower().strip()
                existing = movie_index.get(key)

                if existing:

                    merged = {}

                    for d in existing["downloads"]:
                        merged[d.split("/")[-1].lower()] = d

                    for d in movie["downloads"]:
                        fname = d.split("/")[-1].lower()
                        merged[fname] = d

                    existing["downloads"] = list(merged.values())

                else:

                    movie.pop("url", None)
                    new_movies.append(movie)
                    movie_index[key] = movie

                    print("New:", movie["name"])

    # ---------- FINAL CLEAN ----------
    clean_db = {}

    for m in new_movies + database:
        key = m["name"].lower().strip()

        if key not in clean_db:
            clean_db[key] = m
        else:
            merged = {}

            for d in clean_db[key]["downloads"]:
                merged[d.split("/")[-1].lower()] = d

            for d in m["downloads"]:
                merged[d.split("/")[-1].lower()] = d

            clean_db[key]["downloads"] = list(merged.values())

    save_database(list(clean_db.values()))

    print("\nDone ✅ New movies:", len(new_movies))

# ---------- RUN ----------
if __name__ == "__main__":

    start = time.time()

    run_scraper()

    end = time.time()

    print("\nFinished in", round(end - start, 2), "seconds")
