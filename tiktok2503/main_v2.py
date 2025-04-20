from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TikTokMobileCrawler:
    def __init__(self, headless=False):
        options = self.get_mobile_chrome_options(headless)
        self.driver = webdriver.Chrome(options=options)
        self.actions = ActionChains(self.driver)

    def get_mobile_chrome_options(self, headless=False):
        mobile_emulation = {
            "deviceName": "iPhone X"
        }
        options = Options()
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if headless:
            options.add_argument("--headless")
        return options

    def login_manual(self):
        print("[*] Opening login page. Please login manually.")
        self.driver.get("https://www.tiktok.com/login")
        time.sleep(30)  # Let user manually log in (QR code or password)
        print("[+] Login assumed complete.")

    def get_url(self, url):
        self.driver.get(url)
        time.sleep(5)
        self._handle_captcha_if_any()

    def _handle_captcha_if_any(self):
        try:
            captcha_present = self.driver.find_element(By.ID, "captcha-verify-page")
            print("[!] Captcha detected! Please solve manually.")
            WebDriverWait(self.driver, 180).until_not(
                EC.presence_of_element_located((By.ID, "captcha-verify-page"))
            )
            print("[+] Captcha solved.")
        except:
            print("[*] No captcha detected.")

    def open_comments(self):
        print("[*] Looking for mobile comment button...")
        try:
            comment_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-e2e="comment-button-icon"]'))
            )
            comment_button.click()
            print("[+] Comment section opened.")
            time.sleep(3)
        except Exception as e:
            print(f"[-] Failed to click comment button: {e}")

    def scroll_comments(self, max_scrolls=30, patience=5):
        prev_count = 0
        stagnant_count = 0

        for i in range(max_scrolls):
            try:
                comment_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-e2e="comment-item"]')
                current_count = len(comment_elements)

                if current_count == prev_count:
                    stagnant_count += 1
                    print(f"[=] No new comments (x{stagnant_count})")
                else:
                    stagnant_count = 0
                    print(f"[+] New comments loaded: {current_count - prev_count}")
                    prev_count = current_count

                if stagnant_count >= patience:
                    print("[*] No more comments loading. Stopping scroll.")
                    break

                # Scroll comment list by JS (mobile style)
                self.driver.execute_script("window.scrollBy(0, window.innerHeight * 0.5);")
                time.sleep(2)
            except Exception as e:
                print("[-] Error during scroll:", e)
                break

    def extract_comments(self):
        comments = []
        try:
            comment_divs = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-e2e="comment-item"]')
            for div in comment_divs:
                try:
                    author = div.find_element(By.CSS_SELECTOR, 'span[data-e2e="comment-user-username"]').text
                    content = div.find_element(By.CSS_SELECTOR, 'p[data-e2e="comment-level-content"]').text
                    comments.append((author, content))
                except Exception:
                    continue
        except Exception as e:
            print("[-] Error extracting comments:", e)
        return comments

    def quit(self):
        self.driver.quit()
        print("[*] Driver closed.")


# === Example usage ===
if __name__ == "__main__":
    url = "https://www.tiktok.com/@samsung/video/7472975780897688852"

    crawler = TikTokMobileCrawler(headless=False)
    crawler.login_manual()  # only needed first time if not logged in
    crawler.get_url(url)
    crawler.open_comments()
    crawler.scroll_comments(max_scrolls=30, patience=3)
    comments = crawler.extract_comments()
    crawler.quit()

    for i, (author, text) in enumerate(comments[:10], 1):
        print(f"{i}. @{author}: {text}")
