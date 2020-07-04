import requests
from flask import request


class TelegramBot:

    def __init__(self):
        self.api_url = False
        self.post = False
        self.file_url = False

    def login(self, token):
        self.api_url = 'https://api.telegram.org/bot{}/'.format(token)
        self.file_url = 'https://api.telegram.org/file/bot{}/'.format(token)

    def get_updates(self):
        """ Только если не включены WebHooks """
        if self.api_url:
            url = self.api_url + 'getUpdates'
            r = requests.get(url)
            return r.json()

    def send_message(self, chat_id, text):
        if self.api_url:
            url = self.api_url + 'sendMessage'
            message = {'chat_id': chat_id, 'text': text}
            requests.post(url, json=message)

    def get_json_post(self):
        r = request.get_json()
        is_bot = r['message']['from']['is_bot']
        if not is_bot:
            self.post = r
            return self.post


    @property
    def message_type(self):
        if self.post:
            if self.post['message'].get('text'):
                mtype = 'text'
            elif self.post['message'].get('photo'):
                mtype = 'photo'
            else:
                mtype = None
            return mtype

    @property
    def photo_id(self):
        if self.message_type == 'photo':
            return self.post['message']['photo'][-1]['file_id']

    @property
    def chat_id(self):
        if self.post:
            return self.post['message']['chat']['id']

    @property
    def text_message(self):
        if self.post and self.post['message'].get('text'):
                return self.post['message']['text']

    def download_file(self, file_id, filename_path):
        if self.api_url:
            url = self.api_url + 'getFile?file_id={}'.format(file_id)
            r = requests.get(url)
            json_data = r.json()
            if json_data.get('ok'):
                file_path = json_data['result']['file_path']
                download_url = self.file_url + file_path
                file = requests.get(download_url)
                with open(filename_path, 'wb') as f:
                    f.write(file.content)

    def send_photo(self, chat_id, photo_path):
        url = self.api_url + 'sendPhoto'
        with open(photo_path, 'rb') as f:
            photo = {'photo': f}
            requests.post(url + '?chat_id={}'.format(chat_id), files=photo)
