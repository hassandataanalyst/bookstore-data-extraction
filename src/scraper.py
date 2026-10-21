import logging
import time
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import settings
from src.parser import parse_listing, parse_product

logger = logging.getLogger(__name__)


def make_session():
    session = requests.Session()
    session.headers.update({"User-Agent": "BookstorePortfolioResearch/1.0 (educational scraping practice)"})
    retry = Retry(total=settings.MAX_RETRIES, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    return session


def scrape_catalog():
    session = make_session()
    page_url = settings.BASE_URL
    page_count = 0
    visited_pages = set()
    product_urls = []
    allowed_host = urlparse(settings.BASE_URL).hostname
    while page_url and (settings.MAX_PAGES is None or page_count < settings.MAX_PAGES):
        if page_url in visited_pages:
            logger.warning("Repeated catalog page: %s", page_url)
            break
        if urlparse(page_url).hostname != allowed_host:
            raise ValueError(f"Unexpected catalog host: {page_url}")
        visited_pages.add(page_url)
        logger.info("Catalog page %s: %s", page_count + 1, page_url)
        response = session.get(page_url, timeout=settings.TIMEOUT_SECONDS)
        response.raise_for_status()
        urls, page_url = parse_listing(response.text, response.url)
        product_urls.extend(urls)
        page_count += 1
        time.sleep(settings.REQUEST_DELAY_SECONDS)

    unique_urls = list(dict.fromkeys(product_urls))
    logger.info("Catalog pages=%s; unique product URLs=%s", page_count, len(unique_urls))
    records = []
    failures = []
    for index, url in enumerate(unique_urls, 1):
        try:
            if urlparse(url).hostname != allowed_host:
                raise ValueError("Product URL outside allowed host")
            response = session.get(url, timeout=settings.TIMEOUT_SECONDS)
            response.raise_for_status()
            records.append(parse_product(response.text, response.url))
            logger.info("Product %s/%s: %s", index, len(unique_urls), url)
        except (requests.RequestException, ValueError, TypeError) as exc:
            logger.error("Failed %s: %s", url, exc)
            failures.append({"product_url": url, "error": str(exc)})
        time.sleep(settings.REQUEST_DELAY_SECONDS)
    return records, failures, page_count, len(unique_urls)
