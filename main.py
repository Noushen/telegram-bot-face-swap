import flask
from flask import request
from flask import jsonify
import cv2

from bot_class import TelegramBot
from face_swap.pretty_face_swap import pretty_face_swap
from face_swap.ugly_face_swap import ugly_face_swap


with open('token') as f:
    TOKEN = f.read()

DOWNLOAD_FOLDER = 'temp_photos/'
OUTPUT_PATH = DOWNLOAD_FOLDER + 'result.jpg'
PREDICTOR_PATH = 'models/shape_predictor_68_face_landmarks.dat'

app = flask.Flask(__name__)
bot = TelegramBot()
bot.login(TOKEN)
last_message_on_chat_id = {}
type_face_swap = {}


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = bot.get_json_post()

        if bot.message_type == 'text':
            if bot.text_message == '/start':
                last_message_on_chat_id[bot.chat_id] = 1
                bot.send_message(bot.chat_id,
                                 'Приветсвую. Отправьте первую фотографию. '
                                 'С этой фотографии будет взято лицо')

            elif bot.text_message == '/pretty':
                type_face_swap[bot.chat_id] = False
                bot.send_message(bot.chat_id, 'Вы выбрали вариант с частичной заменой лица')

            elif bot.text_message == '/ugly':
                type_face_swap[bot.chat_id] = True
                bot.send_message(bot.chat_id, 'Вы выбрали вариант с полной заменой лица')

            elif bot.text_message == '/swap':
                if last_message_on_chat_id.get(bot.chat_id) == 3:
                    if type_face_swap.get(bot.chat_id):
                        result_img = ugly_face_swap(DOWNLOAD_FOLDER + '{}_1.jpg'.format(bot.chat_id),
                                                    DOWNLOAD_FOLDER + '{}_2.jpg'.format(bot.chat_id),
                                                    PREDICTOR_PATH)
                        cv2.imwrite(OUTPUT_PATH, result_img)
                        bot.send_photo(bot.chat_id, OUTPUT_PATH)

                    else:
                        result_img = pretty_face_swap(DOWNLOAD_FOLDER + '{}_1.jpg'.format(bot.chat_id),
                                                      DOWNLOAD_FOLDER + '{}_2.jpg'.format(bot.chat_id),
                                                      PREDICTOR_PATH)
                        cv2.imwrite(OUTPUT_PATH, result_img)
                        bot.send_photo(bot.chat_id, OUTPUT_PATH)

                else:
                    bot.send_message(bot.chat_id,
                                     'Вы ещё не отправили фотографии.\n'
                                     'Введите команду - /start'
                                     'И отправьте по очереди фотографии')

        elif bot.message_type == 'photo':

            if last_message_on_chat_id.get(bot.chat_id) == 1:
                last_message_on_chat_id[bot.chat_id] = 2
                bot.download_file(bot.photo_id, '{}_1.jpg'.format(bot.chat_id), DOWNLOAD_FOLDER)
                bot.send_message(bot.chat_id,
                                 'Отправьте вторую фотографию. '
                                 'На эту фотографию будет перенесено лицо.')

            elif last_message_on_chat_id.get(bot.chat_id) == 2:
                last_message_on_chat_id[bot.chat_id] = 3
                bot.download_file(bot.photo_id, '{}_2.jpg'.format(bot.chat_id), DOWNLOAD_FOLDER)
                bot.send_message(bot.chat_id,
                                 'Можете выбрать вариант замены лица:\n'
                                 '1. Частичная замена лица. Используется по умолчанию.\n'
                                 'Команда - /pretty\n'
                                 '2. Полная замена лица. Могут быть артефакты в виде линий.\n'
                                 'Команда - /ugly\n\n'
                                 'Для запуска замены лица введите команду - /swap')

        return jsonify(r)

    return '<h1>Hello My app</h1>'



if __name__ == '__main__':
    app.run()

