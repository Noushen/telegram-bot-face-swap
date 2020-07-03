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

first_photo_flag = {}
second_photo_flag = {}
type_swap_flag = {}
current_step = {}


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = bot.get_json_post()

        if bot.message_type == 'text':
            if bot.text_message == '/start':
                current_step[bot.chat_id] = 1
                bot.send_message(bot.chat_id,
                                 'Приветсвую.\n'
                                 'Этот бот может переносить лицо с одной фотографии на лицо другой фотографии.\n'
                                 'Отправьте первую фотографию. '
                                 'С этой фотографии будет взято лицо')

            elif bot.text_message == '/pretty':
                type_swap_flag[bot.chat_id] = False
                bot.send_message(bot.chat_id,
                                 'Вы выбрали вариант с частичной заменой лица\n'
                                 'Если все фотографии загружены используйте команду\n'
                                 '/swap')

            elif bot.text_message == '/ugly':
                type_swap_flag[bot.chat_id] = True
                bot.send_message(bot.chat_id,
                                 'Вы выбрали вариант с полной заменой лица\n'
                                 'Если все фотографии загружены используйте команду\n'
                                 '/swap')

            elif bot.text_message == '/change_source_photo':
                current_step[bot.chat_id] = 4
                bot.send_message(bot.chat_id, 'Отправьте фотографию откуда будет взято лицо')

            elif bot.text_message == '/change_target_photo':
                current_step[bot.chat_id] = 5
                bot.send_message(bot.chat_id, 'Отправьте фотографию куда будет перенесено лицо')

            elif bot.text_message == '/swap':
                if current_step.get(bot.chat_id) == 3:
                    if type_swap_flag.get(bot.chat_id):
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

            if current_step.get(bot.chat_id) == 1:
                current_step[bot.chat_id] = 2
                bot.download_file(bot.photo_id, '{}_1.jpg'.format(bot.chat_id), DOWNLOAD_FOLDER)
                first_photo_flag[bot.chat_id] = True
                bot.send_message(bot.chat_id,
                                 'Отправьте вторую фотографию. '
                                 'На эту фотографию будет перенесено лицо.')

            elif current_step.get(bot.chat_id) == 2:
                current_step[bot.chat_id] = 3
                bot.download_file(bot.photo_id, '{}_2.jpg'.format(bot.chat_id), DOWNLOAD_FOLDER)
                second_photo_flag[bot.chat_id] = True
                bot.send_message(bot.chat_id,
                                 'Можете выбрать вариант замены лица:\n'
                                 '1. Частичная замена лица. Используется по умолчанию.\n'
                                 'Команда - /pretty\n'
                                 '2. Полная замена лица. Могут быть артефакты в виде линий.\n'
                                 'Команда - /ugly\n\n'
                                 'Для запуска замены лица введите команду - /swap')

            elif current_step.get(bot.chat_id) == 4:
                current_step[bot.chat_id] = 3
                bot.download_file(bot.photo_id, '{}_1.jpg'.format(bot.chat_id), DOWNLOAD_FOLDER)
                first_photo_flag[bot.chat_id] = True
                bot.send_message(bot.chat_id, 'Фотография источник была заменена.')

            elif current_step.get(bot.chat_id) == 5:
                current_step[bot.chat_id] = 3
                bot.download_file(bot.photo_id, '{}_2.jpg'.format(bot.chat_id), DOWNLOAD_FOLDER)
                first_photo_flag[bot.chat_id] = True
                bot.send_message(bot.chat_id, 'Целевая фотография была заменена.')

        return jsonify(r)

    return '<h1>Hello My app</h1>'



if __name__ == '__main__':
    app.run()

