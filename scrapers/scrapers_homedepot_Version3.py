import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import clean_price

class HomeDepotScraper:
    TP_NAME = "Home Depot"

    def __init__(self, driver):
        self.driver = driver

    def extract_price(self, url, keyword):
        self.driver.get(url)

        wait = WebDriverWait(self.driver, 25)
        h1 = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        title_text = h1.text.strip()

        if keyword and keyword.lower() not in title_text.lower():
            raise Exception(f"Validación fallida: '{keyword}' no encontrada en '{title_text}'")

        time.sleep(3)

        candidates = []
        selectors = [
            "[data-testid*='price']",
            "[class*='price']",
            "[class*='Price']",
            "span",
            "div",
        ]

        for selector in selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                txt = el.text.strip()
                css_class = (el.get_attribute("class") or "").lower()
                if "$" in txt and len(txt) < 40:
                    candidates.append({"text": txt, "class": css_class})

        valid_prices = []
        for item in candidates:
            css_class = item["class"]
            txt = item["text"]

            if any(word in css_class for word in ["old", "strike", "list", "before"]):
                continue

            price = clean_price(txt)
            if price is not None:
                valid_prices.append(price)

        if not valid_prices:
            raise Exception("No se encontró precio publicado válido")

        return {
            "title": title_text,
            "price": min(valid_prices),
        }