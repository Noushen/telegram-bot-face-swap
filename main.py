import flask
from flask import request
from flask import jsonify
import cv2

from bot_class import TelegramBot
from face_swap.pretty_face_swap import pretty_face_swap
from face_swap.pretty_face_swap import find_face
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
                                 'Для начала отправьте первую фотографию. '
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

            elif bot.text_message == '/change_photo_1':
                current_step[bot.chat_id] = 4
                bot.send_message(bot.chat_id, 'Отправьте фотографию откуда будет взято лицо')

            elif bot.text_message == '/change_photo_2':
                current_step[bot.chat_id] = 5
                bot.send_message(bot.chat_id, 'Отправьте фотографию куда будет перенесено лицо')

            elif bot.text_message == '/swap':
                if first_photo_flag.get(bot.chat_id) and second_photo_flag.get(bot.chat_id):
                #if current_step.get(bot.chat_id) == 3:

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

                    bot.send_message(bot.chat_id, 'Готово!\n'
                                                  'Можете попробовать это с другими фотографиями '
                                                  'или другим типом замены лица:\n'
                                                  '/pretty - изменить тип замены лица на частичную\n'
                                                  '/ugly - изменить тип замены лица на полную\n'
                                                  '/change_photo_1 - изменить фотографию источник (1)'                                                  
                                                  '/change_photo_2 - изменить целевую фотографию (2)')

                elif first_photo_flag.get(bot.chat_id):
                    bot.send_message(bot.chat_id, 'Нет целевой фотографии (2)\n'
                                                  'Для заливки введите команду - /change_photo_2')

                elif second_photo_flag.get(bot.chat_id):
                    bot.send_message(bot.chat_id, 'Нет фотографии источника (1)\n'
                                                  'Для заливки введите команду - /change_photo_1')

                else:
                    bot.send_message(bot.chat_id,
                                     'Вы ещё не отправили фотографии.\n'
                                     'Введите команду - /start'
                                     'И отправьте по очереди фотографии')

        elif bot.message_type == 'photo':

            if current_step.get(bot.chat_id) == 1:
                source_photo_name = DOWNLOAD_FOLDER + '{}_1.jpg'.format(bot.chat_id)
                bot.download_file(bot.photo_id, source_photo_name)
                source_img = cv2.imread(source_photo_name)
                if find_face(source_img):
                    current_step[bot.chat_id] = 2
                    first_photo_flag[bot.chat_id] = True
                    bot.send_message(bot.chat_id,
                                     'Первая фотография загружена.\n'
                                     'Отправьте вторую фотографию - '
                                     'на которую будет перенесено лицо.')
                else:
                    first_photo_flag[bot.chat_id] = False
                    bot.send_message(bot.chat_id,
                                     'Не найдено лицо на фотографии. Попробуйте загрузить другое фото.')

            elif current_step.get(bot.chat_id) == 2:
                target_photo_name = DOWNLOAD_FOLDER + '{}_2.jpg'.format(bot.chat_id)
                bot.download_file(bot.photo_id, target_photo_name)
                target_img = cv2.imread(target_photo_name)

                if find_face(target_img):
                    current_step[bot.chat_id] = 3
                    second_photo_flag[bot.chat_id] = True
                    bot.send_message(bot.chat_id,
                                     'Можете выбрать вариант замены лица:\n'
                                     '1. Частичная замена лица. Используется по умолчанию.\n'
                                     'Команда - /pretty\n'
                                     '2. Полная замена лица. Могут быть артефакты в виде линий.\n'
                                     'Команда - /ugly\n\n'
                                     'Для запуска замены лица введите команду - /swap')
                else:
                    second_photo_flag[bot.chat_id] = False
                    bot.send_message(bot.chat_id,
                                     'Не найдено лицо на фотографии. Попробуйте загрузить другое фото.')

            elif current_step.get(bot.chat_id) == 4:
                source_photo_name = DOWNLOAD_FOLDER + '{}_1.jpg'.format(bot.chat_id)
                bot.download_file(bot.photo_id, source_photo_name)
                source_img = cv2.imread(source_photo_name)
                if find_face(source_img):
                    current_step[bot.chat_id] = 3
                    first_photo_flag[bot.chat_id] = True
                    bot.send_message(bot.chat_id, 'Фотография источник была заменена.\n'
                                                  'Теперь можете:\n'
                                                  '/swap - запуск замены лица\n'
                                                  '/pretty - изменить тип замены лица на частичную\n'
                                                  '/ugly - изменить тип замены лица на полную\n'
                                                  '/change_photo_2 - изменить целевую фотографию (2)')
                else:
                    first_photo_flag[bot.chat_id] = False
                    bot.send_message(bot.chat_id,
                                     'Не найдено лицо на фотографии. Попробуйте загрузить другое фото.')

            elif current_step.get(bot.chat_id) == 5:
                target_photo_name = DOWNLOAD_FOLDER + '{}_2.jpg'.format(bot.chat_id)
                bot.download_file(bot.photo_id, target_photo_name)
                target_img = cv2.imread(target_photo_name)
                if find_face(target_img):
                    current_step[bot.chat_id] = 3
                    second_photo_flag[bot.chat_id] = True
                    bot.send_message(bot.chat_id, 'Целевая фотография была заменена.\n'
                                                  'Теперь можете:\n'
                                                  '/swap - запуск замены лица\n'
                                                  '/pretty - изменить тип замены лица на частичную\n'
                                                  '/ugly - изменить тип замены лица на полную\n'
                                                  '/change_photo_1 - изменить фотографию источник (1)')
                else:
                    second_photo_flag[bot.chat_id] = False
                    bot.send_message(bot.chat_id,
                                     'Не найдено лицо на фотографии. Попробуйте загрузить другое фото.')

        return jsonify(r)

    return '<h1>Hello My app</h1>'



if __name__ == '__main__':
    app.run()

