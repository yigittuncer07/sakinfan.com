import httpx
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Global cache variables
_concerts_cache = []
_last_fetch_time = None
_CACHE_DURATION = timedelta(days=1)
_fetch_lock = asyncio.Lock()

async def get_upcoming_concerts() -> list[dict]:
    global _concerts_cache, _last_fetch_time
    
    now = datetime.now()
    
    # return cached data if it's still valid
    if _last_fetch_time and (now - _last_fetch_time) < _CACHE_DURATION:
        return _concerts_cache

    # use a lock so if 10 users hit the index at the exact time the cache expires,
    # only 1 request goes to the external server, while the other 9 wait.
    async with _fetch_lock:
        # Double-check inside the lock in case another request just updated it
        if _last_fetch_time and (now - _last_fetch_time) < _CACHE_DURATION:
            return _concerts_cache
            
        url = "https://biletinial.com/tr-tr/artist/onur-ozdemir"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                
            if response.status_code != 200:
                return _concerts_cache  # on failure, return stale cache rather than breaking the page

            soup = BeautifulSoup(response.text, "html.parser")
            concert_nodes = soup.select(".ed-biletler__sehir__gun")
            
            concerts = []
            for node in concert_nodes:
                name_tag = node.select_one(".artistProfile_card_item_content_details_name")
                date_tag = node.select_one(".artistProfile_card_item_content_details span")
                venue_tag = node.select_one("address[itemprop='name']")
                price_tag = node.select_one(".price-info")
                
                if name_tag and date_tag and venue_tag:
                    concerts.append({
                        "title": name_tag.text.strip(),
                        "date": date_tag.text.strip(),
                        "venue": venue_tag.text.strip(),
                        "price": price_tag.text.strip() if price_tag else "N/A",
                        "link": f"https://biletinial.com{name_tag['href']}"
                    })
            
            # update cache variables
            _concerts_cache = concerts
            _last_fetch_time = now
            
            return _concerts_cache
        except Exception as e:
            # if the external site is down, return the last known good state
            return _concerts_cache