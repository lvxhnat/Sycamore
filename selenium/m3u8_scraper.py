import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response


def condition_to_retrieve(x):
    try:
        return 'Network.response' in x['method'] and 'm3u8' in x['params']['response']['url']
    except:
        return False


def retrieve_m3u8_url():

    URL = "https://watchnewslive.tv/watch-cnbc-live-stream-free-24-7/"
    IFRAME_XPATH = "/html/body/div[1]/div[1]/div/div[1]/div/article/div/div[3]/div[1]/iframe"
    USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'

    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent = ' + USER_AGENT)

    driver = webdriver.Chrome(ChromeDriverManager(
    ).install(), options=options, desired_capabilities=caps)
    driver.get(URL)

    element_present = EC.presence_of_element_located((By.XPATH, IFRAME_XPATH))
    element = WebDriverWait(driver, 5).until(element_present)
    element.click()

    time.sleep(5)

    browser_log = driver.get_log("performance")

    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event['params']['response']['url']
              for event in events if condition_to_retrieve(event)]

    return events
