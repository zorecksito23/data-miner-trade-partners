from sheets_client import SheetsClient
from utils import now_parts
from scrapers.base import build_driver
from scrapers.homedepot import HomeDepotScraper

def main():
    print("=== INICIANDO SCRAPER HOME DEPOT ===")
    sheets = SheetsClient()
    rows = sheets.get_skus()

    driver = build_driver()
    scraper = HomeDepotScraper(driver)

    try:
        for row in rows:
            tp = str(row.get("TP", "")).strip()
            url = str(row.get("URL del Producto", "")).strip()
            sku = str(row.get("SKU", "")).strip()
            keyword = str(row.get("PALABRA_VALIDACION", "")).strip()

            if tp.lower() != "home depot":
                continue

            if not url or not sku:
                continue

            parts = now_parts()

            try:
                result = scraper.extract_price(url, keyword)

                sheets.append_precio([
                    parts["year"],
                    parts["week"],
                    parts["day"],
                    parts["mmddyy"],
                    tp,
                    sku,
                    result["price"],
                    "N/A",
                    "N/A",
                ])

                print(f"OK | {tp} | {sku} | {result['price']}")

            except Exception as e:
                sheets.append_error([
                    parts["timestamp"],
                    tp,
                    sku,
                    url,
                    str(e),
                ])
                print(f"ERROR | {tp} | {sku} | {e}")

    finally:
        driver.quit()
        print("=== PROCESO FINALIZADO ===")

if __name__ == "__main__":
    main()