from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ItemType(Enum):
    RATED = "rated"
    WATCHLIST = "watchlist"

@dataclass
class RssItem:
    type: ItemType
    title: str
    link: str
    description_html: str
    pub_date_str: Optional[str] = None
    guid_text: Optional[str] = None
    poster_url: Optional[str] = None