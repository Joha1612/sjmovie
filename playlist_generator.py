# import json
#
# INPUT="database.json"
# OUTPUT="netflix_playlist.m3u"
#
# with open(INPUT,"r") as f:
#     data=json.load(f)
#
# with open(OUTPUT,"w") as m3u:
#
#     m3u.write("#EXTM3U\n")
#
#     for movie in data:
#
#         name=movie["name"]
#         poster=movie["poster"]
#         category=movie["category"]
#
#         for link in movie["downloads"]:
#
#             m3u.write(
#                 f'#EXTINF:-1 tvg-logo="{poster}" group-title="{category}",{name}\n'
#             )
#
#             m3u.write(link+"\n")
#
# print("Playlist created")

import json

INPUT="database.json"
OUTPUT="netflix_playlist.m3u"

with open(INPUT,"r",encoding="utf-8") as f:
    data=json.load(f)

with open(OUTPUT,"w",encoding="utf-8") as m3u:

    m3u.write("#EXTM3U\n")

    for movie in data:

        name=movie["name"]
        poster=movie["poster"]
        category=movie["category"]

        for link in movie["downloads"]:

            m3u.write(
                f'#EXTINF:-1 tvg-logo="{poster}" group-title="{category}",{name}\n'
            )

            m3u.write(link+"\n")

print("Playlist generated successfully")