import re
import time
from selenium.webdriver.common.by import By


class HomeDepotScraper:
    def __init__(self, driver, timeout=25):
        self.driver = driver
        self.timeout = timeout

    def _get_text_if_exists(self, by, selector):
        try:
            el = self.driver.find_element(by, selector)
            text = el.text.strip()
            print(f"[HD] Texto encontrado en {selector}: {text}", flush=True)
            return text
        except Exception:
            print(f"[HD] No se encontró texto en {selector}", flush=True)
            return ""

    def _extract_digits(self, text):
        return re.findall(r"\d[\d,]*", text or "")

    def _to_float(self, raw):
        if not raw:
            return None
        raw = raw.replace(",", "").strip()
        try:
            return float(raw)
        except Exception:
            return None

    def _extract_precio_contado(self):
        text = self._get_text_if_exists(By.CSS_SELECTOR, "#offerPrice")
        if not text:
            raise Exception("No se encontró el precio contado en #offerPrice")

        print(f"[HD] Texto bruto precio contado: {text}", flush=True)

        nums = self._extract_digits(text)
        if not nums:
            raise Exception(f"No se pudo parsear el precio contado desde: '{text}'")

        return self._to_float(nums[0])

    def _extract_msi(self):
        text = self._get_text_if_exists(By.CSS_SELECTOR, "#openMSIDetail")
        print(f"[HD] Texto bruto MSI: {text}", flush=True)

        if not text:
            return "", None

        nums = self._extract_digits(text)
        pago_plazo = self._to_float(nums[0]) if len(nums) >= 1 else None

        plazo_match = re.search(r"(\d+)\s*MSI", text, re.IGNORECASE)
        plazo = f"{plazo_match.group(1)} MSI" if plazo_match else ""

        return plazo, pago_plazo

    def extract_price(self, url, keyword):
        try:
            print(f"[HD] Abriendo URL: {url}", flush=True)
            self.driver.get(url)
            time.sleep(3)

            precio_contado = self._extract_precio_contado()
            print(f"[HD] Precio contado extraído: {precio_contado}", flush=True)

            plazo_text, pago_plazo = self._extract_msi()
            print(f"[HD] MSI extraído: plazo={plazo_text}, pago_plazo={pago_plazo}", flush=True)

            product_model = self._get_text_if_exists(By.CSS_SELECTOR, "#productModel")
            product_sku = self._get_text_if_exists(By.CSS_SELECTOR, "#productSku")

            keyword_norm = (keyword or "").strip().lower()
            model_norm = product_model.lower()
            sku_norm = product_sku.lower()

            if keyword_norm:
                found_in_model = keyword_norm in model_norm
                found_in_sku = keyword_norm in sku_norm

                print(
                    f"[HD] Validando keyword='{keyword}' contra "
                    f"productModel='{product_model}' y productSku='{product_sku}'",
                    flush=True
                )

                if not found_in_model and not found_in_sku:
                    raise Exception(
                        f"Validación fallida. '{keyword}' no se encontró ni en "
                        f"productModel='{product_model}' ni en productSku='{product_sku}'"
                    )

            result = {
                "price": precio_contado,
                "plazo": plazo_text,
                "pago_plazo": pago_plazo,
            }

            print(f"[HD] Resultado final: {result}", flush=True)
            return result

        except Exception as e:
            page_title = ""
            current_url = ""

            try:
                page_title = self.driver.title
            except Exception:
                pass

            try:
                current_url = self.driver.current_url
            except Exception:
                pass

            raise Exception(
                f"{type(e).__name__}: {e} | title='{page_title}' | current_url='{current_url}'"
            )
