import json
import const
from datetime import datetime

DISCOVER_URL = "https://bandcamp.com/api/discover/3/get_web"

def load_template():
    with open("item.rss", "r", encoding="utf-8") as f:
        return f.read()


def fetch_albums(genre="all", fmt="digital", sort="rand", page=1):
    params = {
        "g": genre,
        "f": fmt,
        "s": sort,
        "p": page
    }

    response = const.requester.get(DISCOVER_URL, params=params, timeout=15)

    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        print("Response preview:", response.text[:500])
        return []

    content_type = response.headers.get('Content-Type', '')
    if 'application/json' not in content_type and 'text/javascript' not in content_type:
        print(f"Warning: Response is not JSON (Content-Type: {content_type})")
        return []

    try:
        data = response.json()
    except Exception as e:
        print(f"JSON decode error: {e}")
        print("Response text:", response.text[:500])
        return []

    items = data.get("items", [])
    albums = []

    for item in items:
        if item.get("type") != "a":
            continue

        title = item.get("primary_text", "")
        artist = item.get("secondary_text", "")
        genre_text = item.get("genre_text", "")
        art_id = item.get("art_id")

        if not title:
            continue

        url_hints = item.get("url_hints", {})
        subdomain = url_hints.get("subdomain", "")
        slug = url_hints.get("slug", "")

        if subdomain and slug:
            album_url = f"https://{subdomain}.bandcamp.com/album/{slug}"
        else:
            continue

        icon = ""
        if art_id:
            icon = f"https://f4.bcbits.com/img/a{art_id}_10.jpg"

        display_title = title
        if genre_text:
            display_title = f"[{genre_text}] {title}"

        pub_date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

        albums.append({
            "title": display_title,
            "item_link": album_url,
            "guid": album_url,
            "links": f"{title} by {artist}",
            "date": pub_date,
            "icon": icon,
            "artist": artist,
            "genre": genre_text
        })

    print(f"Fetched {len(albums)} albums from page {page}")
    return albums[:10]


def generate_feed(albums, output_file="../feeds/bandcamp_discover.xml"):
    template = load_template()
    items_xml = ""

    for album in albums:
        icon = album.get("icon", "")
        if icon:
            album["icon_html"] = (
                f'<img src="{icon}" style="max-width:100%;height:auto;'
                f'display:block;margin-bottom:10px;" /><br />'
            )
        else:
            album["icon_html"] = ""

        item_content = template
        for key, value in album.items():
            item_content = item_content.replace(f"{{{{{key}}}}}", str(value))
        items_xml += item_content + "\n"

    now = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    full_rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Bandcamp Discover</title>
    <link>https://bandcamp.com/discover/all/digital?s=rand</link>
    <description>Daily discovers from Bandcamp</description>
    <lastBuildDate>{now}</lastBuildDate>
    {items_xml}
  </channel>
</rss>"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_rss)

    print(f"RSS feed generated: {output_file} ({len(albums)} items)")


if __name__ == "__main__":
    albums = fetch_albums()
    if albums:
        generate_feed(albums)
    else:
        print("No albums found.")