import pandas as pd


def validate_products(df: pd.DataFrame):
    required = ["upc", "title", "category", "price_gbp", "rating", "product_url"]
    missing_counts = {col: int(df[col].isna().sum()) for col in df.columns}
    problems = []
    if df.empty:
        problems.append("Dataset is empty")
    for col in required:
        if df[col].isna().any() or df[col].astype("string").str.strip().eq("").any():
            problems.append(f"Missing required values: {col}")
    if df["product_url"].duplicated().any():
        problems.append("Duplicate product URLs")
    if df["upc"].dropna().duplicated().any():
        problems.append("Duplicate UPCs")
    if (~df["price_gbp"].between(0, float("inf"))).fillna(True).any():
        problems.append("Invalid prices")
    if (~df["rating"].between(1, 5)).fillna(True).any():
        problems.append("Invalid ratings")
    if (~df["stock_quantity"].between(0, 10**9)).fillna(False).any():
        problems.append("Negative stock quantity")
    return {"rows": len(df), "missing_counts": missing_counts, "problems": problems, "passed": not problems}
