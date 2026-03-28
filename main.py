import requests
from utils import now_parts
from scrapers.base import build_driver
from scrapers.homedepot import HomeDepotScraper
from config import APPS_SCRIPT_URL

def obtener_skus():
    response = requests.get(f"{APPS_SCRIPT_URL}?action=skus", timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("productos", [])

def guardar_precio(payload):
    response = requests.post(f"{APPS_SCRIPT_URL}?action=price", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

def guardar_error(payload):
    response = requests.post(f"{APPS_SCRIPT_URL}?action=error", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

def main():
    print("=== INICIANDO SCRAPER HOME DEPOT ===")
    productos = obtener_skus()

    driver = build_driver()
    scraper = HomeDepotScraper(driver)

    try:
        for prod in productos:
            tp = str(prod.get("tp", "")).strip()
            url = str(prod.get("url", "")).strip()
            sku = str(prod.get("sku", "")).strip()
            keyword = str(prod.get("keyword", "")).strip()

            if tp.lower() != "home depot":
                continue

            if not url or not sku:
                continue

            parts = now_parts()

            try:
                result = scraper.extract_price(url, keyword)

                guardar_precio({
                    "anio": parts["year"],
                    "semana": parts["week"],
                    "dia": parts["day"],
                    "fecha": parts["mmddyy"],
                    "tp": tp,
                    "sku": sku,
                    "precioContado": result["price"],
                    "semanalidad": "N/A",
                    "plazo": "N/A"
                })

                print(f"OK | {tp} | {sku} | {result['price']}")

            except Exception as e:
                guardar_error({
                    "fecha": parts["timestamp"],
                    "tp": tp,
                    "sku": sku,
                    "url": url,
                    "error": str(e)
                })

                print(f"ERROR | {tp} | {sku} | {e}")

    finally:
        driver.quit()
        print("=== PROCESO FINALIZADO ===")

if __name__ == "__main__":
    main()
