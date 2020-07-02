import flask
from flask import request
from flask import jsonify
import json


from bot_class import TelegramBot


with open('token') as f:
    TOKEN = f.read()


def write_json(data, filename='answer.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


app = flask.Flask(__name__)
bot = TelegramBot()
bot.login(TOKEN)
last_message_on_chat_id = {}


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = bot.get_json_post()
        print(last_message_on_chat_id)

        if bot.message_type == 'text':
            if bot.text_message == '/start':
                last_message_on_chat_id[bot.chat_id] = 1
                bot.send_message(bot.chat_id, 'Приветсвую. Отправьте первую фотографию')

        elif bot.message_type == 'photo':
            if last_message_on_chat_id.get(bot.chat_id) == 1:
                last_message_on_chat_id[bot.chat_id] = 2
                bot.download_file(bot.photo_id, '{}_1'.format(bot.chat_id))
                bot.send_message(bot.chat_id, 'Отправьте вторую фотографию')
            elif last_message_on_chat_id.get(bot.chat_id) == 2:
                last_message_on_chat_id[bot.chat_id] = 3
                bot.download_file(bot.photo_id, '{}_2'.format(bot.chat_id))
                bot.send_message(bot.chat_id, 'Подождите результат')

        return jsonify(r)

    return '<h1>Hello My app</h1>'



if __name__ == '__main__':
    app.run()

