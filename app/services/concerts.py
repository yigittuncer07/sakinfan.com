import httpx
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

_concerts_cache = []
_last_fetch_time = None
_CACHE_DURATION = timedelta(days=1)
_fetch_lock = asyncio.Lock()

def _parse_date_for_sorting(date_str: str) -> tuple:
    # example format: "04 Ekim Pazar, 22:00"
    tr_months = {
        "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6,
        "Temmuz": 7, "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12
    }
    try:
        parts = date_str.replace(",", "").split()
        day = int(parts[0])
        month = tr_months.get(parts[1], 12)
        
        # Handle time if present
        hour, minute = 0, 0
        if len(parts) >= 4 and ":" in parts[3]:
            hour, minute = map(int, parts[3].split(":"))

        # if the concert month is much earlier than the current month (e.g., Jan vs current Oct), 
        # it likely belongs to the next year.
        current_month = datetime.now().month
        year_offset = 1 if month < (current_month - 2) else 0

        return (year_offset, month, day, hour, minute)
    except Exception:
        # if parsing fails, push it to the bottom
        return (99, 99, 99, 0, 0)

async def get_upcoming_concerts() -> list[dict]:
    global _concerts_cache, _last_fetch_time
    
    now = datetime.now()
    
    if _last_fetch_time and (now - _last_fetch_time) < _CACHE_DURATION:
        return _concerts_cache

    async with _fetch_lock:
        if _last_fetch_time and (now - _last_fetch_time) < _CACHE_DURATION:
            return _concerts_cache
            
        url = "https://biletinial.com/tr-tr/artist/onur-ozdemir"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                
            if response.status_code != 200:
                return _concerts_cache

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
            
            # sort chronologically before caching
            concerts.sort(key=lambda x: _parse_date_for_sorting(x["date"]))
            
            _concerts_cache = concerts
            _last_fetch_time = now
            
            return _concerts_cache
        except Exception:
            return _concerts_cache