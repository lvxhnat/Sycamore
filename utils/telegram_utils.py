import os
import requests
import dotenv
import logging

dotenv.load_dotenv()


class TelegramBot:

    def __init__(self):

        self.token = os.environ['TELEGRAM_TOKEN']
        self.default_chat_id = os.environ['TELEGRAM_SYCAMORE_CHAT_ID']

    def send_message(self, text: str, chat_id: str = None):
        ''' Sends a basic message 
        '''
        if chat_id is None:
            url_req = "https://api.telegram.org/bot" + self.token + \
                "/sendMessage" + "?chat_id=" + self.default_chat_id + "&text=" + text
        else:
            url_req = "https://api.telegram.org/bot" + self.token + \
                "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
        try:
            results = requests.get(url_req)
            return results.json()

        except Exception as e:
            logging.error(f"Telegram Bot [MESSAGE]: {e}")
