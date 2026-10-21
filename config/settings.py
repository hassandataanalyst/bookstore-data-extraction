from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
BASE_URL = "https://books.toscrape.com/"
MAX_PAGES = None  # Set to None for the entire catalog after testing.
TIMEOUT_SECONDS = 20
MAX_RETRIES = 3
REQUEST_DELAY_SECONDS = 0.5
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
LOG_DIR = BASE_DIR / "logs"
