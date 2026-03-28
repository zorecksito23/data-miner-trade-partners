import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HomeDepotScraper:
    TP_NAME = "Home Depot"

    def __init__(self, driver):
        self.driver = driver

    def _clean_price_from_text(self, text):
        if not text:
            return None

        normalized = text.replace("\n", " ").replace("\xa0", " ").strip()

        # Busca formatos como 13,299 o 13,299.00
        match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', normalized)
        if not match:
            return None

        raw = match.group(1).replace(",", "")
        try:
            return float(raw)
        except ValueError:
            return None

    def extract_price(self, url, keyword):
        self.driver.get(url)

        wait = WebDriverWait(self.driver, 30)
        time.sleep(5)

        # 1. TÍTULO
        try:
            title_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#productTitle"))
            )
            title_text = title_elem.text.strip()
        except Exception:
            title_text = self.driver.title.strip()

        if keyword and keyword.lower() not in title_text.lower():
            raise Exception(
                f"Validación fallida: '{keyword}' no encontrada en '{title_text}'"
            )

        # 2. PRECIO PUBLICADO
        price_text = ""

        # Intento principal: bloque exacto del precio vigente
        try:
            price_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#offerPrice"))
            )
            price_text = price_elem.text.strip()
        except Exception:
            pass

        # Intento secundario por si el bloque existe pero el texto viene fragmentado
        if not price_text:
            try:
                container = self.driver.find_element(By.CSS_SELECTOR, "#productPrice")
                price_text = container.text.strip()
            except Exception:
                pass

        price_value = self._clean_price_from_text(price_text)

        if price_value is None:
            raise Exception(
                f"No se encontró precio publicado válido. Texto detectado: '{price_text}'"
            )

        return {
            "title": title_text,
            "price": price_value,
        }
