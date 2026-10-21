import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_listing(html: str, page_url: str):
    soup = BeautifulSoup(html, "html.parser")
    products = []
    for item in soup.select("article.product_pod"):
        link = item.select_one("h3 a")
        if link and link.get("href"):
            products.append(urljoin(page_url, link["href"]))
    next_link = soup.select_one("li.next a")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None
    return products, next_url


def parse_product(html: str, product_url: str):
    soup = BeautifulSoup(html, "html.parser")
    title_node = soup.select_one("div.product_main h1")
    price_node = soup.select_one("div.product_main p.price_color")
    rating_node = soup.select_one("div.product_main p.star-rating")
    stock_node = soup.select_one("div.product_main p.availability")
    description_node = soup.select_one("#product_description + p")
    crumbs = soup.select("ul.breadcrumb li a")
    category = crumbs[-1].get_text(strip=True) if len(crumbs) >= 3 else None
    details = {}
    for row in soup.select("table.table.table-striped tr"):
        key = row.select_one("th")
        value = row.select_one("td")
        if key and value:
            details[key.get_text(strip=True)] = value.get_text(strip=True)
    classes = rating_node.get("class", []) if rating_node else []
    rating = next((RATING_MAP[c] for c in classes if c in RATING_MAP), None)
    availability = stock_node.get_text(" ", strip=True) if stock_node else None
    stock_match = re.search(r"\((\d+) available\)", availability or "")
    image = soup.select_one("div.item.active img")
    return {
        "upc": details.get("UPC"),
        "title": title_node.get_text(strip=True) if title_node else None,
        "category": category,
        "price_gbp": price_node.get_text(strip=True) if price_node else None,
        "rating": rating,
        "availability": availability,
        "stock_quantity": int(stock_match.group(1)) if stock_match else None,
        "review_count": details.get("Number of reviews"),
        "description": description_node.get_text(" ", strip=True) if description_node else None,
        "product_url": product_url,
        "image_url": urljoin(product_url, image["src"]) if image and image.get("src") else None,
    }
