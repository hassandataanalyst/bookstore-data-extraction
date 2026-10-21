import pandas as pd


def clean_products(records):
    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError("No products extracted; check site access and parsing selectors.")
    for column in ("upc", "title", "category", "availability", "description", "product_url", "image_url"):
        df[column] = df[column].astype("string").str.strip()
    df["price_gbp"] = pd.to_numeric(df["price_gbp"].astype("string").str.replace(r"[^\d.]", "", regex=True), errors="coerce")
    for column in ("rating", "stock_quantity", "review_count"):
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")
    df = df.drop_duplicates(subset=["product_url"], keep="first").reset_index(drop=True)
    df["scraped_at_utc"] = pd.Timestamp.now(tz="UTC").isoformat()
    return df
