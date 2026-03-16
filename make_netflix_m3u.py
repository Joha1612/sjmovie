import json

INPUT_JSON = "movies.json"
OUTPUT_M3U = "netflix_playlist.m3u"

with open(INPUT_JSON,"r",encoding="utf-8") as f:
    data=json.load(f)

with open(OUTPUT_M3U,"w",encoding="utf-8") as m3u:

    m3u.write("#EXTM3U\n")

    for movie in data:

        name=movie.get("name","Unknown")

        for q in movie.get("qualities",[]):

            quality=q.get("quality","HD")
            link=q.get("download")

            if not link:
                continue

            m3u.write(f'#EXTINF:-1 group-title="Movies",{name} ({quality})\n')
            m3u.write(link+"\n")

print("Netflix style playlist created")