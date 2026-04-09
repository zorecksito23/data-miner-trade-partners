import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HomeDepotScraper:
    def __init__(self, driver, timeout=25):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _get_text_if_exists(self, by, selector):
        try:
            el = self.driver.find_element(by, selector)
            return el.text.strip()
        except Exception:
            return ""

    def _clean_number(self, text):
        if not text:
            return None

        cleaned = re.sub(r"[^\d.]", "", str(text))
        if not cleaned:
            return None

        try:
            return float(cleaned)
        except ValueError:
            return None

    def extract_price(self, url, keyword):
        self.driver.get(url)

        price_text = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".price-format__main-price"))
        ).text.strip()

        plazo_text = self._get_text_if_exists(By.CSS_SELECTOR, ".credit-offer__term")
        pago_plazo_text = self._get_text_if_exists(By.CSS_SELECTOR, ".credit-offer__amount")

        product_model = self._get_text_if_exists(By.CSS_SELECTOR, "#productModel")
        product_sku = self._get_text_if_exists(By.CSS_SELECTOR, "#productSku")

        keyword_norm = (keyword or "").strip().lower()
        model_norm = product_model.lower()
        sku_norm = product_sku.lower()

        if keyword_norm:
            found_in_model = keyword_norm in model_norm
            found_in_sku = keyword_norm in sku_norm

            if not found_in_model and not found_in_sku:
                raise Exception(
                    f"Validación fallida. '{keyword}' no se encontró ni en "
                    f"productModel='{product_model}' ni en productSku='{product_sku}'"
                )

        return {
            "price": self._clean_number(price_text),
            "plazo": plazo_text,
            "pago_plazo": self._clean_number(pago_plazo_text),
        }
