import requests
import const
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

URL = const._bandcampDailyUrl
HEADERS = const._bandcampUserAgent

def fetch_articles():
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    articles = []
    
    article_divs = soup.select("div.list-article")
    
    if not article_divs:
        print("Warning: No articles found")
        return []
    
    seen_links = set()
    
    for article_div in article_divs:
        # Find the title link within each list-article div
        title_link = article_div.select_one("div.title-wrapper a.title")
        
        # Fallback to any link if title link not found
        if not title_link:
            title_link = article_div.select_one("a[href]")
        
        if not title_link:
            continue
        
        href = title_link["href"]
        
        # Skip duplicates
        if href in seen_links:
            continue
        seen_links.add(href)    
        
        # Normalize href
        if not href.startswith("http"):
            if href.startswith("/"):
                href = f"https://daily.bandcamp.com{href}"
            else:
                continue
        
        # Get title from the title link
        title = title_link.get_text(strip=True)
        if not title or len(title) < 5:
            continue
        
        # Extract the franchise/category
        franchise_tag = article_div.select_one("a.franchise")
        franchise_text = ""
        if franchise_tag:
            franchise_text = franchise_tag.get_text(strip=True).upper()
        
        # Append franchise to title if it's ALBUM OF THE DAY
        if franchise_text == "ALBUM OF THE DAY":
            title = f"[Album of the Day] {title}"
        
        description = title
        pub_date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        icon = ""
        
        # Extract Date from article-info-text
        info_text = article_div.select_one("div.article-info-text")
        if info_text:
            text_content = info_text.get_text()
            date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\s\d{4}', text_content)
            if date_match:
                try:
                    parsed_date = datetime.strptime(date_match.group(0), "%B %d, %Y")
                    pub_date = parsed_date.strftime("%a, %d %b %Y %H:%M:%S +0000")
                except ValueError:
                    pass
        
        # Extract Icon/Image from the thumb link
        thumb_link = article_div.select_one("a.thumb img")
        if thumb_link:
            src = thumb_link.get("src")
            
            if src:
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = f"https://daily.bandcamp.com{src}"
                
                icon = src

        articles.append({
            "title": title,
            "item_link": href,
            "guid": href,
            "links": description,
            "date": pub_date,
            "icon": icon
        })
    
    return articles

def generate_feed(articles, output_file="../feeds/bandcamp_daily.xml"):
    template = const.load_template()
    items_xml = ""
    
    for article in articles:
         # Build icon HTML only if icon exists
        icon = article.get("icon", "")
        if icon:
            article["icon_html"] = f'<img src="{icon}" style="max-width: 100%; height: auto; display: block; margin-bottom: 10px;" /><br />'
        else:
            article["icon_html"] = ""

        item_content = template
        for key, value in article.items():
            item_content = item_content.replace(f"{{{{{key}}}}}", str(value))
        items_xml += item_content + "\n"

    now = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    full_rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Bandcamp Daily Latest</title>
    <link>{URL}</link>
    <description>Bandcamp Daily</description>
    <lastBuildDate>{now}</lastBuildDate>
    {items_xml}
  </channel>
</rss>"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_rss)
    
    print(f"RSS feed generated: {output_file} ({len(articles)} items)")

if __name__ == "__main__":
    articles = fetch_articles()
    if articles:
        generate_feed(articles)
    else:
        print("No articles found.")