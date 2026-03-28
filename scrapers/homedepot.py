import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HomeDepotScraper:
    TP_NAME = "Home Depot"

    def __init__(self, driver):
        self.driver = driver

    def _clean_text(self, value):
        if not value:
            return ""
        return str(value).strip().lower().replace(" ", "")

    def _extract_number(self, text):
        if not text:
            return None

        normalized = text.replace("\n", " ").replace("\xa0", " ").strip()
        match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)', normalized)
        if not match:
            return None

        raw = match.group(1).replace(",", "")
        try:
            return float(raw)
        except ValueError:
            return None

    def _extract_plazo_text(self, text):
        if not text:
            return ""

        normalized = text.replace("\n", " ").replace("\xa0", " ").strip()

        # Busca patrones como 12 MSI, 12 meses, 24 quincenas, 8 semanas
        patterns = [
            r'(\d+\s*MSI)',
            r'(\d+\s*meses?)',
            r'(\d+\s*quincenas?)',
            r'(\d+\s*semanas?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, normalized, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return normalized

    def extract_price(self, url, keyword):
        self.driver.get(url)

        wait = WebDriverWait(self.driver, 30)
        time.sleep(5)

        title_text = ""
        model_text = ""
        price_text = ""

        # Título
        try:
            title_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#productTitle"))
            )
            title_text = title_elem.text.strip()
        except Exception:
            try:
                title_text = self.driver.title.strip()
            except Exception:
                title_text = ""

        # Modelo
        try:
            model_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#productModel"))
            )
            model_text = model_elem.text.strip()
        except Exception:
            model_text = ""

        if keyword:
            if self._clean_text(keyword) != self._clean_text(model_text):
                raise Exception(
                    f"Validación fallida: modelo esperado '{keyword}' "
                    f"pero se encontró '{model_text}'"
                )

        # Precio contado
        try:
            price_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#offerPrice"))
            )
            price_text = price_elem.text.strip()
        except Exception:
            pass

        if not price_text:
            try:
                container = self.driver.find_element(By.CSS_SELECTOR, "#productPrice")
                price_text = container.text.strip()
            except Exception:
                price_text = ""

        precio_contado = self._extract_number(price_text)

        if precio_contado is None:
            raise Exception(
                f"No se encontró precio publicado válido. "
                f"Texto detectado: '{price_text}' | Modelo detectado: '{model_text}'"
            )

        # Plazo / pago de plazo
        pago_plazo = ""
        plazo = ""

        try:
            msi_container = self.driver.find_element(By.CSS_SELECTOR, "#openMSIDetail")
            msi_text = msi_container.text.strip()

            plazo = self._extract_plazo_text(msi_text)

            numbers = re.findall(r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)', msi_text)
            parsed_numbers = []
            for n in numbers:
                try:
                    parsed_numbers.append(float(n.replace(",", "")))
                except:
                    pass

            # Elegimos el primer número decimal/chico que no sea el precio contado
            for n in parsed_numbers:
                if abs(n - precio_contado) > 1:
                    pago_plazo = n
                    break

        except Exception:
            pass

        return {
            "title": title_text,
            "model": model_text,
            "price": precio_contado,
            "plazo": plazo,
            "pago_plazo": pago_plazo,
        }
