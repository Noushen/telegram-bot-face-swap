import flask
from flask import request
from flask import jsonify
import json
import requests

from bot_class import TelegramBot


with open('token') as f:
    TOKEN = f.read()

URL_BOT = 'https://api.telegram.org/bot{}/'.format(TOKEN)


def get_updates():
    url = URL_BOT + 'getUpdates'
    r = requests.get(url)
    return r.json()


def send_message(chat_id, text):
    url = URL_BOT + 'sendMessage'
    message = {'chat_id': chat_id, 'text': text}
    requests.post(url, json=message)


def get_last_chat_id(updates):
    chat_id = updates['result'][-1]['message']['chat']['id']
    return chat_id


def get_chat_id_from_json(data):
    chat_id = data['message']['chat']['id']
    return chat_id


def write_json(data, filename='answer.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def main():
    # updates = get_updates()
    # chat_id = get_last_chat_id(updates)
    # send_message(chat_id, 'Hello')
    bot = TelegramBot()
    bot.login(TOKEN)
    r = bot.get_updates()
    print(r)



app = flask.Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    bot = TelegramBot
    bot.login(TOKEN)


    if request.method == 'POST':
        r = request.get_json()
        # write_json(r)
        return jsonify(r)
    return '<h1>Hello My app</h1>'


if __name__ == '__main__':
    # main()
    app.run()

