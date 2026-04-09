import time
import requests
from requests.exceptions import RequestException
from utils import now_parts
from scrapers.base import build_driver
from scrapers.homedepot import HomeDepotScraper
from config import APPS_SCRIPT_URL

DEFAULT_TIMEOUT = 60
MAX_RETRIES = 3
RETRY_SLEEP = 5


def request_with_retry(method, url, **kwargs):
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[HTTP] {method} {url} intento {attempt}/{MAX_RETRIES}", flush=True)
            response = requests.request(method, url, timeout=DEFAULT_TIMEOUT, **kwargs)
            response.raise_for_status()
            print(f"[HTTP] OK {method} {url}", flush=True)
            return response
        except RequestException as e:
            last_error = e
            print(f"[HTTP] FAIL {method} {url} intento {attempt}/{MAX_RETRIES}: {e}", flush=True)

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_SLEEP)

    raise last_error


def obtener_skus():
    print("[STEP] Obteniendo SKUS...", flush=True)
    response = request_with_retry("GET", f"{APPS_SCRIPT_URL}?action=skus")
    data = response.json()

    if data.get("error"):
        raise Exception(f"Error obteniendo SKUS: {data['error']}")

    productos = data.get("productos", [])
    print(f"[STEP] SKUS obtenidos: {len(productos)}", flush=True)
    return productos


def guardar_precio(payload):
    print(f"[SAVE] Guardando precio para {payload.get('tp')} | {payload.get('sku')}", flush=True)
    response = request_with_retry("POST", f"{APPS_SCRIPT_URL}?action=price", json=payload)
    data = response.json()

    if data.get("error"):
        raise Exception(f"Error guardando precio: {data['error']}")

    print(f"[SAVE] OK guardado precio: {data}", flush=True)
    return data


def guardar_error(payload):
    print(f"[SAVE] Guardando error para {payload.get('tp')} | {payload.get('sku')}", flush=True)
    response = request_with_retry("POST", f"{APPS_SCRIPT_URL}?action=error", json=payload)
    data = response.json()

    if data.get("error"):
        raise Exception(f"Error guardando log: {data['error']}")

    print(f"[SAVE] OK guardado error: {data}", flush=True)
    return data


def main():
    print("=== INICIANDO SCRAPER HOME DEPOT ===", flush=True)

    productos = obtener_skus()

    print("[STEP] Construyendo driver...", flush=True)
    driver = build_driver()
    print("[STEP] Driver listo", flush=True)

    scraper = HomeDepotScraper(driver)
    print("[STEP] Scraper Home Depot listo", flush=True)

    try:
        for idx, prod in enumerate(productos, start=1):
            print(f"[LOOP] Producto {idx}/{len(productos)}", flush=True)

            tp = str(prod.get("tp", "")).strip()
            url = str(prod.get("url", "")).strip()
            sku = str(prod.get("sku", "")).strip()
            keyword = str(prod.get("keyword", "")).strip()

            print(f"[LOOP] tp={tp} | sku={sku} | keyword={keyword} | url={url}", flush=True)

            if tp.lower() != "home depot":
                print("[LOOP] Saltado por TP distinto", flush=True)
                continue

            if not url or not sku:
                print("[LOOP] Saltado por URL/SKU vacío", flush=True)
                continue

            parts = now_parts()

            try:
                print(f"[SCRAPER] Extrayendo producto {sku}", flush=True)
                result = scraper.extract_price(url, keyword)
                print(f"[SCRAPER] Resultado {sku}: {result}", flush=True)

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
                    f"guardado={save_result}",
                    flush=True
                )

            except Exception as e:
                error_msg = f"{type(e).__name__}: {e}"

                try:
                    guardar_error({
                        "fecha": parts["timestamp"],
                        "tp": tp,
                        "sku": sku,
                        "url": url,
                        "error": error_msg
                    })
                except Exception as log_error:
                    print(f"ERROR GUARDANDO LOG | {tp} | {sku} | {log_error}", flush=True)

                print(f"ERROR | {tp} | {sku} | {error_msg}", flush=True)

    finally:
        print("[STEP] Cerrando driver...", flush=True)
        driver.quit()
        print("=== PROCESO FINALIZADO ===", flush=True)


if __name__ == "__main__":
    main()
