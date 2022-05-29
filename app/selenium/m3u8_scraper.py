import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.selenium.base import SeleniumChromeDriver


def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response


def condition_to_retrieve(x):
    try:
        return 'Network.response' in x['method'] and 'm3u8' in x['params']['response']['url']
    except:
        return False


def retrieve_m3u8_url() -> str:

    URL = "https://watchnewslive.tv/watch-cnbc-live-stream-free-24-7/"
    IFRAME_XPATH = "/html/body/div[1]/div[1]/div/div[1]/div/article/div/div[3]/div[1]/iframe"

    driver = SeleniumChromeDriver.generate_chrome_driver()
    driver.get(URL)

    element_present = EC.presence_of_element_located((By.XPATH, IFRAME_XPATH))
    element = WebDriverWait(driver, 5).until(element_present)
    element.click()

    time.sleep(5)

    browser_log = driver.get_log("performance")

    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event['params']['response']['url']
              for event in events if condition_to_retrieve(event)][0]

    return events
