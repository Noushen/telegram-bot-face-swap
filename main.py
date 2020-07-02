import flask
from flask import request
from flask import jsonify
import json
import requests

from bot_class import TelegramBot


with open('token') as f:
    TOKEN = f.read()


def write_json(data, filename='answer.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def main():
    # updates = get_updates()
    # chat_id = get_last_chat_id(updates)
    # send_message(chat_id, 'Hello')
    # bot = TelegramBot()
    # bot.login(TOKEN)
    # r = bot.get_updates()
    # print(r)
    pass


app = flask.Flask(__name__)
bot = TelegramBot()
bot.login(TOKEN)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # r = request.get_json()
        # chat_id = bot.get_chat_id_from_json(r)
        r = bot.get_post()
        print(bot.chat_id)
        print(bot.text_message)
        # write_json(r)
        return jsonify(r)
    return '<h1>Hello My app</h1>'


if __name__ == '__main__':
    # main()
    app.run()

