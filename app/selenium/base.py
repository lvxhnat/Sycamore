import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

environment_loaded = load_dotenv()


class SeleniumChromeDriver:

    def __init__(self, ):

        self.environment = os.getenv("ENVIRONMENT")

    def __generate_chrome_options(self, ):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('user-agent = ' + os.environ['USER_AGENT'])

        if self.environment == "prod":
            chrome_options.binary_location = os.environ.get(
                "GOOGLE_CHROME_SHIM")
            chrome_options.add_argument("--disable-dev-shm-usage")

        return chrome_options

    def generate_chrome_driver(self, type: str):

        if type == "network":
            caps = DesiredCapabilities.CHROME
            caps['goog:loggingPrefs'] = {'performance': 'ALL'}
            return webdriver.Chrome(
                chrome_options=self.__generate_chrome_options(), desired_capabilities=caps)

        else:
            return webdriver.Chrome(chrome_options=self.__generate_chrome_options())
