import requests
from flask import request


class TelegramBot:

    def login(self, token):
        self.api_url = 'https://api.telegram.org/bot{}/'.format(token)

    def get_updates(self):
        """ Только если не включены WebHooks """
        url = self.api_url + 'getUpdates'
        r = requests.get(url)
        return r.json()

    def send_message(self, chat_id, text):
        url = self.api_url + 'sendMessage'
        message = {'chat_id': chat_id, 'text': text}
        requests.post(url, json=message)

    def get_post(self):
        self.post = request.get_json()
        is_bot = self.post['message']['from']['is_bot']
        if not is_bot:
            return self.post

    @property
    def chat_id(self):
        if self.post:
            return self.post['message']['chat']['id']

    @property
    def text_message(self):
        if self.post:
            return self.post['message']['text']
