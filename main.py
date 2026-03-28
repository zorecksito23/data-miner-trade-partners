import requests
from utils import now_parts
from scrapers.base import build_driver
from scrapers.homedepot import HomeDepotScraper
from config import APPS_SCRIPT_URL

def obtener_skus():
    response = requests.get(f"{APPS_SCRIPT_URL}?action=skus", timeout=30)
    response.raise_for_status()
    data = response.json()

    if data.get("error"):
        raise Exception(f"Error obteniendo SKUS: {data['error']}")

    return data.get("productos", [])

def guardar_precio(payload):
    response = requests.post(f"{APPS_SCRIPT_URL}?action=price", json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()

    if data.get("error"):
        raise Exception(f"Error guardando precio: {data['error']}")

    return data

def guardar_error(payload):
    response = requests.post(f"{APPS_SCRIPT_URL}?action=error", json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()

    if data.get("error"):
        raise Exception(f"Error guardando log: {data['error']}")

    return data

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

                save_result = guardar_precio({
                    "anio": parts["year"],
                    "fecha": parts["mmddyy"],
                    "tp": tp,
                    "sku": sku,
                    "precioContado": result["price"],
                    "plazo": result.get("plazo", ""),
                    "pagoPlazo": result.get("pago_plazo", "")
                })

                print(
                    f"OK | {tp} | {sku} | contado={result['price']} | "
                    f"plazo={result.get('plazo', '')} | monto_plazo={result.get('pago_plazo', '')} | "
                    f"guardado={save_result}"
                )

            except Exception as e:
                try:
                    guardar_error({
                        "fecha": parts["timestamp"],
                        "tp": tp,
                        "sku": sku,
                        "url": url,
                        "error": str(e)
                    })
                except Exception as log_error:
                    print(f"ERROR GUARDANDO LOG | {tp} | {sku} | {log_error}")

                print(f"ERROR | {tp} | {sku} | {e}")

    finally:
        driver.quit()
        print("=== PROCESO FINALIZADO ===")

if __name__ == "__main__":
    main()
