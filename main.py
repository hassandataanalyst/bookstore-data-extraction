import json
import logging
import pandas as pd
from config import settings
from src.scraper import scrape_catalog
from src.cleaner import clean_products
from src.validator import validate_products


def main():
    for directory in (settings.RAW_DIR, settings.PROCESSED_DIR, settings.LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", handlers=[logging.StreamHandler(), logging.FileHandler(settings.LOG_DIR / "scraper.log", encoding="utf-8")])
    logger = logging.getLogger(__name__)
    logger.info("Starting bookstore extraction. MAX_PAGES=%s", settings.MAX_PAGES)
    records, failures, pages, discovered = scrape_catalog()
    with (settings.RAW_DIR / "books_raw.json").open("w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)
    with (settings.RAW_DIR / "failed_urls.json").open("w", encoding="utf-8") as file:
        json.dump(failures, file, ensure_ascii=False, indent=2)
    df = clean_products(records)
    report = validate_products(df)
    report.update({"catalog_pages": pages, "discovered_product_urls": discovered, "failed_product_requests": len(failures), "complete_extraction": len(failures) == 0 and len(df) == discovered})
    df.to_csv(settings.PROCESSED_DIR / "books_cleaned.csv", index=False, encoding="utf-8-sig")
    df.to_excel(settings.PROCESSED_DIR / "books_cleaned.xlsx", index=False)
    with (settings.PROCESSED_DIR / "validation_report.json").open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
    logger.info("RESULT | pages=%s | discovered=%s | exported=%s | failed=%s | validation_passed=%s", pages, discovered, len(df), len(failures), report["passed"])
    print("\nOUTPUT:", settings.PROCESSED_DIR)
    print("VALIDATION:", json.dumps(report, indent=2))
    if not report["passed"] or not report["complete_extraction"]:
        raise SystemExit("Extraction completed with validation issues or failed product requests; inspect reports.")


if __name__ == "__main__":
    main()
