import requests


class TelegramBot:

    def login(self, token):
        self.api_url = 'https://api.telegram.org/bot{}/'.format(token)

    def get_updates(self):
        url = self.api_url + 'getUpdates'
        r = requests.get(url)
        return r.json()

    def send_message(self, chat_id, text):
        url = self.api_url + 'sendMessage'
        message = {'chat_id': chat_id, 'text': text}
        requests.post(url, json=message)

    def get_chat_id_from_json(self, data):
        chat_id = data['message']['chat']['id']
        return chat_id