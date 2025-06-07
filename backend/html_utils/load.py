import requests
import urllib3
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

def load_html(url):
    """
    Load page HTML with requests.
    If an error is encountered, retry using Selenium.
    """
    # Adding a real user agent header helps websites accept the page download query
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    # --- Try with requests first ---
    print(f"Loading {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # 403 error = often a bot rejection
        # 400 error = Facebook returns this for invalid requests
        # 429 error = too many requests
        if response.status_code in [403, 400, 429]:
            print(f"Error {response.status_code} → fallback to Selenium")
            return load_with_selenium(url)
        else:
            response.raise_for_status()
            html = response.text
            return html
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.HTTPError) as err:
        print(f"{err} → fallback to Selenium")
        return load_with_selenium(url)


def load_with_selenium(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f"user-agent={USER_AGENT}")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html

