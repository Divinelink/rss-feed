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