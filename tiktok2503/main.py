from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_mobile_chrome_options():
    mobile_emulation = {
        "deviceName": "iPhone X"  # You can try "Pixel 2", "Galaxy S5", etc.
    }
    options = Options()
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return options


class Crawler:
    def __init__(self, headless=False):
        ua = UserAgent()
        user_agent = ua.random

        options = Options()
        options.add_argument(f'user-agent={user_agent}')
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=get_mobile_chrome_options())
        self.actions = ActionChains(self.driver)

    def login_manual(self):
        print("[*] Opening login page. Please login manually.")
        self.driver.get("https://www.tiktok.com/login")
        time.sleep(30)  # give time for manual login
        print("[+] Login completed (assumed)")

    def get_url(self, url: str):
        self.driver.get(url)
        time.sleep(3)
        
        # Check if captcha page is shown
        try:
            captcha_root = self.driver.find_element(By.ID, "captcha-verify-page")
            print("[!] Captcha detected. Please solve it manually...")
            
            # Wait for captcha to disappear
            WebDriverWait(self.driver, 180).until_not(
                EC.presence_of_element_located((By.ID, "captcha-verify-page"))
            )
            print("[+] Captcha cleared!")
        except:
            print("[*] No captcha detected.")


    def wait_for_comment_button(self, timeout=15):
        try:
            comment_button = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-e2e="comment-icon"]'))
            )
            return comment_button
        except Exception:
            print("[-] Timeout waiting for comment button")
            return None


    def open_comments(self):
        print("[*] Trying to click comment button...")
        comment_button = self.wait_for_comment_button()
        if comment_button:
            comment_button.click()
            print("[+] Comment section opened.")
            time.sleep(3)
        else:
            print("[-] Failed to open comment section.")


    def scroll_comments(self, max_scrolls=30, patience=5):
        """
        Scrolls the comment section to load more comments.
        Stops if no new comments are loaded after `patience` tries.
        """
        try:
            comment_container = self.driver.find_element(By.XPATH, '//div[contains(@class, "DivCommentListContainer")]')
        except Exception:
            print("[-] Could not find comment container")
            return

        prev_count = 0
        stagnant_count = 0

        for i in range(max_scrolls):
            # Find all comments currently loaded
            current_comments = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-e2e="comment-item"]')
            current_count = len(current_comments)

            # Check if new comments loaded
            if current_count == prev_count:
                stagnant_count += 1
                print(f"  [=] No new comments (x{stagnant_count})")
            else:
                stagnant_count = 0
                print(f"  [+] New comments loaded: {current_count - prev_count}")
                prev_count = current_count

            if stagnant_count >= patience:
                print("[*] Stopping scroll: no more new comments.")
                break

            # Scroll inside the comment section
            try:
                comment_container = self.driver.find_element(By.XPATH, '//div[contains(@class, "DivCommentListContainer")]')
                self.actions.move_to_element(comment_container).click().send_keys(Keys.END).perform()
                time.sleep(2)
            except Exception:
                print("[-] Comment container not found during scroll")
                break


    def extract_comments(self):
        comments = []
        try:
            comment_divs = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-e2e="comment-item"]')
            for div in comment_divs:
                try:
                    author = div.find_element(By.CSS_SELECTOR, 'a[data-e2e="comment-user-username"]').text
                    content = div.find_element(By.CSS_SELECTOR, 'p[data-e2e="comment-level-content"]').text
                    comments.append((author, content))
                except Exception:
                    continue
        except Exception as e:
            print("[-] Error extracting comments:", e)
        return comments

    def quit(self):
        self.driver.quit()


# === Example usage ===
if __name__ == "__main__":
    url = "https://www.tiktok.com/@samsung/video/7472975780897688852?_r=1&_t=ZS-8vbrJkywLLj"

    try:
        crawler = Crawler(headless=False)
        crawler.login_manual()
        crawler.get_url(url)
        crawler.open_comments()
        crawler.scroll_comments()
        comments = crawler.extract_comments()
        crawler.quit()
    except:
        raise ValueError

    if len(comments) == 0:
        print("[-] No comments found.")
    else:
        for i, (author, text) in enumerate(comments[:10], 1):
            print(f"{i}. @{author}: {text}")
