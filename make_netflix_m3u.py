import json
import os

INPUT_JSON = "movies.json"
OUTPUT_FOLDER = "playlists"

# folder create
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

# category wise group
categories = {}

for movie in data:

    name = movie.get("name", "Unknown")
    category = movie.get("category", "Others")

    if category not in categories:
        categories[category] = []

    for q in movie.get("qualities", []):

        quality = q.get("quality", "HD")
        link = q.get("download")

        if not link:
            continue

        categories[category].append({
            "name": name,
            "quality": quality,
            "link": link
        })

# create separate m3u files
for category, items in categories.items():

    filename = category.replace(" ", "_") + ".m3u"
    filepath = os.path.join(OUTPUT_FOLDER, filename)

    with open(filepath, "w", encoding="utf-8") as m3u:

        m3u.write("#EXTM3U\n")

        for item in items:

            m3u.write(
                f'#EXTINF:-1 group-title="{category}",{item["name"]} ({item["quality"]})\n'
            )
            m3u.write(item["link"] + "\n")

    print(f"Created: {filepath}")

print("\nAll category playlists created ✅")
