import json
import os

INPUT_JSON = "database.json"
OUTPUT_FOLDER = "playlists"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

categories = {}

for movie in data:

    name = movie.get("name", "Unknown")
    category = movie.get("category", "Others")

    if category not in categories:
        categories[category] = []

    for link in movie.get("downloads", []):

        # quality detect (720p / 1080p)
        quality = "HD"
        if "1080" in link:
            quality = "1080p"
        elif "720" in link:
            quality = "720p"
        elif "480" in link:
            quality = "480p"

        categories[category].append({
            "name": name,
            "quality": quality,
            "link": link
        })

# create category wise m3u
for category, items in categories.items():

    filename = category.replace(" ", "_").replace("&", "and") + ".m3u"
    filepath = os.path.join(OUTPUT_FOLDER, filename)

    with open(filepath, "w", encoding="utf-8") as m3u:

        m3u.write("#EXTM3U\n")

        for item in items:

            m3u.write(
                f'#EXTINF:-1 group-title="{category}",{item["name"]} ({item["quality"]})\n'
            )
            m3u.write(item["link"] + "\n")

    print("Created:", filepath)

print("\nAll playlists created ✅")
