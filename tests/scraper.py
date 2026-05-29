import httpx
from bs4 import BeautifulSoup

def fetch_concerts():
    url = "https://biletinial.com/tr-tr/profile/onur-ozdemir"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = httpx.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"Failed to fetch. Status: {response.status_code}"}

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
            
    return concerts

if __name__ == "__main__":
    results = fetch_concerts()
    for concert in results:
        print(concert)