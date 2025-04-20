from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
import time


class Crawler:
    def __init__(self, headless: bool = False):
        # Generate a random user agent
        ua = UserAgent()
        user_agent = ua.random

        chrome_options = Options()
        chrome_options.add_argument(f"user-agent={user_agent}")
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=chrome_options)

    def get_url(self, url: str):
        self.driver.get(url)
        print(f"[+] Loaded URL: {url}")

    def scroll_down(self, num_scrolls: int = 3, pause_time: float = 1.0):
        for i in range(num_scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"  [-] Scrolled down {i+1}/{num_scrolls}")
            time.sleep(pause_time)

    def quit(self):
        self.driver.quit()
        print("[*] Driver closed")


# === Example usage ===
if __name__ == "__main__":
    crawler = Crawler(headless=False)
    crawler.get_url("https://example.com")
    crawler.scroll_down(num_scrolls=5, pause_time=1.5)
    crawler.quit()