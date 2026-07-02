import requests
import const
from bs4 import BeautifulSoup
from datetime import datetime
import os

URL = const._bandcampDailyUrl
HEADERS = const._bandcampUserAgent

def load_template():
    with open("item.rss", "r", encoding="utf-8") as f:
        return f.read()

def fetch_articles():
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    articles = []
    
    # Target the main content area where posts are listed
    # Bandcamp often uses .post-list or similar classes
    post_list = soup.select_one(".post-list, .content-area, main")
    if not post_list:
        post_list = soup
        
    # Look for article blocks or list items that contain links to features/lists
    # Based on the extract, posts are often just text blocks with links
    # We will look for all links that point to /features/, /lists/, etc.
    links = post_list.select("a[href*='/features/'], a[href*='/lists/'], a[href*='/album-of-the-day/'], a[href*='/best-'], a[href*='/prog-is'], a[href*='/tape-label'], a[href*='/scene-report'], a[href*='/the-side-door'], a[href*='/essential-releases']")
    
    seen_links = set()
    
    for link in links:
        href = link["href"]
        if href in seen_links or not href.startswith("/"):
            continue
            
        # Ensure it's a full URL
        if not href.startswith("http"):
            href = f"https://daily.bandcamp.com{href}"
            
        seen_links.add(href)
        
        title = link.get_text(strip=True)
        if not title:
            continue
            
        # Find the parent container to get the date/category
        parent = link.find_parent(["div", "li", "article"])
        description = ""
        pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        if parent:
            # Try to find a date string like "July 02, 2026"
            text_content = parent.get_text()
            # Simple regex for date format Month DD, YYYY
            import re
            date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\s\d{4}', text_content)
            if date_match:
                date_str = date_match.group(0)
                try:
                    parsed_date = datetime.strptime(date_str, "%B %d, %Y")
                    pub_date = parsed_date.strftime("%a, %d %b %Y %H:%M:%S +0000")
                except ValueError:
                    pass
            
            # Use the category (e.g., "ALBUM OF THE DAY") as description if available
            # Or just use the title again if no other text is found
            description = title

        articles.append({
            "title": title,
            "item_link": href,
            "guid": href,
            "links": description,
            "date": pub_date
        })
    
    return articles

def generate_feed(articles, output_file="../feeds/bandcamp_daily.xml"):
    template = load_template()
    items_xml = ""
    
    for article in articles:
        item_content = template
        for key, value in article.items():
            item_content = item_content.replace(f"{{{{{key}}}}}", str(value))
        items_xml += item_content + "\n"

    now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
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