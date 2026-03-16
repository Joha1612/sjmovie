
import json
import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

# ---------- CLOUDFLARE FRIENDLY SESSION ----------

session = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)

DATABASE_FILE = "database.json"

START_PAGE = 1
END_PAGE = 2

MOVIE_THREADS = 8

VIDEO_FORMATS = (".mkv", ".mp4", ".avi", ".mov", ".webm")

CATEGORIES = {
     "Bangla & Kolkata": "https://fibwatch.art/videos/category/1",
    "Web Series": "https://fibwatch.art/videos/category/3",
    "Hindi": "https://fibwatch.art/videos/category/4",
    "Hindi Dubbed": "https://fibwatch.art/videos/category/5",
    "Bangla Dubbed": "https://fibwatch.art/videos/category/852",
    "Natok": "https://fibwatch.art/videos/category/855",
}

lock = threading.Lock()

# ---------- DATABASE ----------

def load_database():

    try:
        with open(DATABASE_FILE,"r",encoding="utf-8") as f:
            return json.load(f)

    except:
        return []


def save_database(data):

    with open(DATABASE_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=4,ensure_ascii=False)


# ---------- SAFE REQUEST ----------

def safe_request(url,retries=4):

    for i in range(retries):

        try:

            r = session.get(url,timeout=20)

            if r.status_code == 200:
                return r

        except Exception:
            print("Retry request:",url)

        time.sleep(2)

    print("Failed request:",url)

    return None


# ---------- GET WATCH LINKS ----------

def get_watch_links(base_url):

    links = []

    for page in range(START_PAGE,END_PAGE+1):

        url = f"{base_url}?page_id={page}"

        print("Scanning:",url)

        r = safe_request(url)

        if not r:
            continue

        soup = BeautifulSoup(r.text,"lxml")

        for a in soup.select("a[href*='/watch/']"):

            link = urljoin(url,a["href"])

            link = link.split("?")[0].rstrip("/")

            if link not in links:
                links.append(link)

    print("Total watch pages:",len(links))

    return links

# ---------- EXTRACT DOWNLOAD LINKS ----------

def extract_downloads(soup):

    downloads = set()

    for a in soup.find_all("a",href=True):

        href = a["href"].strip()

        lower = href.lower()

        if any(ext in lower for ext in VIDEO_FORMATS):

            if "urlshortlink" in lower:
                continue

            if "b-cdn.net" not in lower:
                continue

            downloads.add(href)

    return list(downloads)


# ---------- SCRAPE MOVIE ----------

def scrape_movie(url):

    time.sleep(0.5)

    r = safe_request(url)

    if not r:
        return None

    soup = BeautifulSoup(r.text,"lxml")

    title = soup.find("title")

    if not title:
        print("No title:",url)
        return None

    name = title.text.split("-")[0].strip()

    poster = None

    meta = soup.find("meta",property="og:image")

    if meta:
        poster = meta.get("content")

    downloads = extract_downloads(soup)

    return {
        "name":name,
        "poster":poster,
        "downloads":downloads,
        "url":url
    }


# ---------- MAIN SCRAPER ----------

def run_scraper():

    database = load_database()

    movie_index = {m["name"]:m for m in database}

    new_movies = []

    retry_movies = []

    for category,url in CATEGORIES.items():

        print("\nCategory:",category)

        watch_links = get_watch_links(url)

        with ThreadPoolExecutor(max_workers=MOVIE_THREADS) as executor:

            futures = [executor.submit(scrape_movie,link) for link in watch_links]

            for future in as_completed(futures):

                movie = future.result()

                if not movie:
                    continue

                movie["category"] = category

                if not movie["downloads"]:

                    print("Download link not found (first try):",movie["name"])

                    retry_movies.append(movie["url"])

                    continue


                existing = movie_index.get(movie["name"])

                if existing:

                    existing["downloads"].extend(movie["downloads"])
                    existing["downloads"] = list(set(existing["downloads"]))

                else:

                    movie.pop("url",None)

                    new_movies.append(movie)

                    movie_index[movie["name"]] = movie

                    print("New movie:",movie["name"])


    # ---------- RETRY MISSING MOVIES ----------

    if retry_movies:

        print("\nRetrying missing movies...\n")

        time.sleep(3)

        with ThreadPoolExecutor(max_workers=3) as executor:

            futures = [executor.submit(scrape_movie,link) for link in retry_movies]

            for future in as_completed(futures):

                movie = future.result()

                if not movie:
                    continue

                if not movie["downloads"]:

                    print("Download link not found (final):",movie["name"])

                    continue


                movie.pop("url",None)

                existing = movie_index.get(movie["name"])

                if existing:

                    existing["downloads"].extend(movie["downloads"])
                    existing["downloads"] = list(set(existing["downloads"]))

                else:

                    new_movies.append(movie)

                    movie_index[movie["name"]] = movie

                    print("Recovered movie:",movie["name"])


    database = new_movies + database

    save_database(database)

    print("\nNew movies added:",len(new_movies))


# ---------- RUN ----------

if __name__ == "__main__":

    start = time.time()

    run_scraper()

    end = time.time()

    print("\nFinished in",round(end-start,2),"seconds")