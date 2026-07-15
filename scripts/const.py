import cloudscraper

# Bandcamp
_bandcampDailyUrl = "https://daily.bandcamp.com/latest"
_bandcampUserAgent = {"User-Agent": "Mozilla/5.0 (compatible; BandcampRSSBot/1.0)"}
# TMDB
_tmdbBaseV4Url = "https://api.themoviedb.org/4"
_tmdbPosterPath = "https://image.tmdb.org/t/p/w500"

requester = cloudscraper.create_scraper(
    session_refresh_interval=300,
    enable_stealth=True,
    stealth_options={
        'min_delay': 4.0,
        'max_delay': 6.0,
        'human_like_delays': True,
        'randomize_headers': True,
        'browser_quirks': True
    },
)

def load_template(**kwargs):
    with open("item.rss", "r", encoding="utf-8") as f:
        template = f.read()
    
    # Handle player_html conditionally
    player_html = kwargs.get('player_html', '')
    kwargs['audio_player'] = f'<br />{player_html}' if player_html else ''
    kwargs.pop('player_html', None)
    
    # Replace all placeholders
    for key, value in kwargs.items():
        template = template.replace(f'{{{{{key}}}}}', str(value))
    
    return template