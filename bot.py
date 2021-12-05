# Импортируем библиотеки:
import os
import re
import time

import telebot
from telebot import types

from google.cloud import dialogflow
from google.api_core.exceptions import InvalidArgument


# Токен Бота:
bot = telebot.TeleBot('5071288099:AAHV62fPQgGAvrXaXcZKUT3tD4u6HEmzN6I')
FeedbackID = '988304573'


# Клавиатуры:

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.row('Стать волонтёром', 'Оставить комментарий')
keyboard.add('Связь с разработчиками')

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.row('Заполнить анкету', 'Я прошёл курс обучения')  # 'Перейти к курсу'
markup.add('Главное меню')

application = types.ReplyKeyboardMarkup(resize_keyboard=True)
application.row('Оформить заявку', 'Я оформил заявку')
application.add('Главное меню')

videoKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
videoKeyboard.row('Загрузить видео', 'Пропустить этот шаг')
videoKeyboard.add('Главное меню')

recommendationKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
recommendationKeyboard.row('Загрузить рекомендации/благодарности', 'У меня нет рекомендаций')
recommendationKeyboard.add('Главное меню')

insuranceKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
insuranceKeyboard.row('Загрузить справку или расписку', 'У меня нет справки/расписки')
insuranceKeyboard.add('Главное меню')

yesNoKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
yesNoKeyboard.row('Да', 'Нет')
yesNoKeyboard.add('Главное меню')

contractKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
contractKeyboard.add('Загрузить скан договора', 'Главное меню')

kordons = types.ReplyKeyboardMarkup(resize_keyboard=True)
kordons.row('"Озёрный" кордон', 'Кордон "Травяной"')
kordons.add('Кордон "Долина Гейзеров"', 'Кордон "Узон"')
kordons.add('Кордон "Исток и Аэродром"', 'Кордон "Кроноки и Семячик"')

processingKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
processingKeyboard.row('Я согласен', 'Я не согласен')

# Интеграция с DialogFlow:
def textMessage(message):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'wisewolfbot-elfd-91c71082c820.json'

    DIALOGFLOW_PROJECT_ID = 'wisewolfbot-elfd'
    DIALOGFLOW_LANGUAGE_CODE = 'ru'
    SESSION_ID = 'Wolf9000'

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
    text_input = dialogflow.TextInput({"text": message.text, "language_code": DIALOGFLOW_LANGUAGE_CODE})
    query_input = dialogflow.QueryInput({"text": text_input})
    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
    except InvalidArgument:
        raise

    print("Query text:", response.query_result.query_text)
    print("Detected intent:", response.query_result.intent.display_name)
    print("Detected intent confidence:", response.query_result.intent_detection_confidence)
    if response.query_result.fulfillment_text == "":
        return "Прости, я не понял тебя. Я ещё учусь, и могу не распознать некорорые фразы. Попробуй сформулировать мысль иначе."
    return response.query_result.fulfillment_text


# Обработчик команд бота:
@bot.message_handler(content_types=['text'])
def keyboard_commands(message):
    if message.text == '/start':
        msg = bot.send_message(message.chat.id,
                               'Привет! Я Мудрый Волк Камчатки. Бот, который поможет Вам стать волонтёром Кронского заповедника!',
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)

    elif message.text == "Стать волонтёром":
        bot.send_message(message.chat.id,
                         'Для постановки в график прохождения волонтерских работ на территории Кроноцкого государственного заповедника/Южно-Камчатского федерального заказника Вам необходимо:')
        time.sleep(1)
        bot.send_message(message.chat.id,
                         'Заполнить анкету на прохождение обучения в Школе Защитников Природы')
        time.sleep(1)
        msg = bot.send_message(message.chat.id,
                               'Пройти курс, по окончании которого у Вас будет итоговый тест, в случае успешного результата Вас перенаправят в отдел познавательного туризма',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, keyboard_commands)

    elif message.text == "Заполнить анкету":
        msg = bot.send_message(message.chat.id, 'Продолжая, Вы принимаете соглашение на обработку персональных данных. Вы согласны?',reply_markup=processingKeyboard)
        bot.register_next_step_handler(msg, data_processing)

    elif message.text == "Перейти к курсу":
        msg = bot.send_message(message.chat.id,
                               'Перейти к курсу: https://kronoki.ru/ru/volunteerism/request',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, keyboard_commands)

    elif message.text == "Я прошёл курс обучения":
        msg = bot.send_message(message.chat.id,
                               'Отлично! Теперь выберите, оформляли ли Вы заявку:',
                               reply_markup=application)
        bot.register_next_step_handler(msg, application_check)

    elif message.text == 'Загрузить видео':
        msg = bot.send_message(message.chat.id,
                               '''Загрузите видео ниже. Бот отправит его организаторам''',
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, video_check)

    elif message.text == 'Оставить комментарий':
        msg = bot.send_message(message.chat.id, 'Напишите комментарий:')
        bot.register_next_step_handler(msg, save_comment)

    elif message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               'Главное меню',
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)

    elif message.text == 'Связь с разработчиками':
        msg = bot.send_message(message.chat.id,
                               '''Теперь напишите текст Вашего сообщения (отзыв, ошибка, вопрос или предложение).
Ваше сообщение будет доставлено разработчикам.''',
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, feedback)

    else:
        bot.send_message(message.chat.id, textMessage(message))


def save_comment(message):
    if not os.path.isdir("users/" + str(message.chat.id)):
        os.mkdir("users/" + str(message.chat.id))
        os.mkdir("users/" + str(message.chat.id) + '/recommendation')
        os.mkdir("users/" + str(message.chat.id) + '/insurance')
        os.mkdir("users/" + str(message.chat.id) + '/contract')
        os.mkdir("users/" + str(message.chat.id) + '/video')
    file = open("users/" + str(message.chat.id) + '/Комментарий.txt', 'w')
    file.write(message.text)
    msg = bot.send_message(message.chat.id, 'Комментарий успешно сохранён. Спасибо!', reply_markup=keyboard)
    bot.register_next_step_handler(msg, keyboard_commands)


def feedback(message):
    bot.send_message(FeedbackID,
                               f'''Обратная связь от {message.from_user.first_name} {message.from_user.last_name}, id: {message.from_user.id}: \n
{message.text}''')
    msg = bot.send_message(message.chat.id,
                               '''Спасибо! Ваше сообщение доставлено разработчикам.''',
                               reply_markup=keyboard)    
    bot.register_next_step_handler(msg, keyboard_commands)

def application_check(message):
    if message.text == 'Оформить заявку':
        msg = bot.send_message(message.chat.id, 'Укажите Ваше ФИО в именительном падеже',)
        bot.register_next_step_handler(msg, fio)

    elif message.text == 'Я оформил заявку':
        msg = bot.send_message(message.chat.id,
                               '''Заявок всегда в десятки раз больше, чем мест. Мы тщательно отбираем волонтеров, учитываем их образование, профессию, наличие рекомендаций от других заповедников и личные качества. Дистанционно выбрать подходящего человека бывает сложно, поэтому мы рады, когда вы сопровождаете заявки короткими видео о себе (на 1-2 минуты)''',
                               reply_markup=videoKeyboard)
        bot.register_next_step_handler(msg, application_check)

    elif message.text == 'Загрузить видео':
        msg = bot.send_message(message.chat.id,
                               '''Загрузите видео ниже. Бот отправит его организаторам''',
                               reply_markup=videoKeyboard)
        bot.register_next_step_handler(msg, video_check)
    elif message.text == 'Пропустить этот шаг':
        msg = bot.send_message(message.chat.id,
                               'Если у вас есть рекомендации или благодарности, загрузите их пожалуйста по одной',
                               reply_markup=recommendationKeyboard)
        bot.register_next_step_handler(msg, application_check)

    elif message.text == "Загрузить рекомендации/благодарности":
        msg = bot.send_message(message.chat.id,
                               '''Загрузите фотографию ниже''',
                               reply_markup=recommendationKeyboard)
        bot.register_next_step_handler(msg, image_check)

    elif message.text == "У меня нет рекомендаций":
        msg = bot.send_message(message.chat.id,
                               '''У вас есть волонтёрская книжка?''',
                               reply_markup=yesNoKeyboard)
        bot.register_next_step_handler(msg, application_check)

    elif message.text == "Загрузить справку или расписку":
        msg = bot.send_message(message.chat.id,
                               'Загрузите фотографию ниже',
                               reply_markup=insuranceKeyboard)
        bot.register_next_step_handler(msg, insurance_check)
    elif message.text == "У меня нет справки/расписки":
        bot.send_message(message.chat.id, "И последний шаг - договор. Высылаем его ниже:")
        msg = bot.send_message(message.chat.id,
                               'Внимательно изучив все пункты договора и его приложений, Вы высылаете нам скан-копию '
                               'подписанного документа',
                               reply_markup=contractKeyboard)
        bot.register_next_step_handler(msg, application_check)

    elif message.text == 'Загрузить скан договора':
        msg = bot.send_message(message.chat.id, 'Загрузите фотографию ниже')
        bot.register_next_step_handler(msg, contract_check)

    elif message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
    else:
        try:
            if message.text.lower() == "да" or message.text.lower() == "нет":
                bot.send_message(message.chat.id, "Пора переходить к следующему шагу:")
                msg = bot.send_message(message.chat.id,
                                       'При наличии, просьба предоставить справки о прохождении медицинской комиссии, если проходили в течение последнего года, или предоставить расписку о состоянии здоровья (ограничения, хронические заболевания) \nПредоставить туристическую страховку',
                                       reply_markup=insuranceKeyboard)
                bot.register_next_step_handler(msg, application_check)
            else:
                bot.send_message(message.chat.id, textMessage(message))
        except AttributeError as e:
            print(e)

# Соглашение на обработку персональных данных:
def data_processing(message):
    if message.text == 'Я согласен':
        bot.send_message(message.chat.id, 'Начинаю тестирование:')
        msg = bot.send_message(message.chat.id, 'Укажите Ваше ФИО в именительном падеже', reply_markup=application)
        bot.register_next_step_handler(msg, fio)
    elif message.text == 'Я не согласен':
        msg = bot.send_message(message.chat.id, 'Тогда оформить заявку Вы можете по ссылке: https://docs.google.com/forms/d/e/1FAIpQLSe1gyTpb69_1pNQPa3bFChFebvAfFMMDyBSWL9cUeRJqLSBWQ/viewform',
        reply_markup=application)

# Анкета:
def fio(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)

    else:
        if re.match('[а-яА-Я ]{' + str(len(message.text)) + ',' + str(len(message.text)) + '}', message.text) is None:
            msg = bot.send_message(message.chat.id, 'Введите корректное ФИО')
            bot.register_next_step_handler(msg, fio)
            return
        else:
            if not os.path.isdir("users/" + str(message.chat.id)):
                os.mkdir("users/" + str(message.chat.id))
                os.mkdir("users/" + str(message.chat.id) + '/recommendation')
                os.mkdir("users/" + str(message.chat.id) + '/insurance')
                os.mkdir("users/" + str(message.chat.id) + '/contract')
                os.mkdir("users/" + str(message.chat.id) + '/video')
            file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'w')
            file.write("ФИО: " + str(message.text) + '\n')
            msg = bot.send_message(message.chat.id, 'Укажите Вашу электронную почту:')
            bot.register_next_step_handler(msg, email)

def email(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
        
    else:
        if re.match('\w*@\w*\.\w*', message.text) is None:
            msg = bot.send_message(message.chat.id, 'Введите корректный email')
            bot.register_next_step_handler(msg, email)
            return
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Почта: " + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Теперь укажите Вашу дату рождения:')
        bot.register_next_step_handler(msg, phone)


def phone(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
        
    else:
        if re.match('\d{2}\.\d{2}\.\d{4}', message.text) is None:
            msg = bot.send_message(message.chat.id, 'Введите корректную дату')
            bot.register_next_step_handler(msg, phone)
            return
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Дата рождения: " + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Ваш номер телефона?')
        bot.register_next_step_handler(msg, education)


def education(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
        
    else:
        if re.match('\d{11,11}', message.text) is None:
            msg = bot.send_message(message.chat.id, 'Введите корректный телефонный номер')
            bot.register_next_step_handler(msg, education)
            return
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Телефон: " + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Ваше образование?')
        bot.register_next_step_handler(msg, territory)


def territory(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
        
    else:
        if re.match('[\w\s- .,]{' + str(len(message.text)) + '}', message.text) is None:
            msg = bot.send_message(message.chat.id, 'Введите корректные данные об образовании')
            bot.register_next_step_handler(msg, territory)
            return
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Образование: " + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Желаемая территория для осуществления волонтёрских работ?', reply_markup=kordons)
        bot.register_next_step_handler(msg, data)


def data(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
        
    else:
        if message.text not in ['"Озёрный" кордон', 'Кордон "Травяной"', 'Кордон "Долина Гейзеров"', 'Кордон "Узон"', 'Кордон "Исток и Аэродром"', 'Кордон "Кроноки и Семячик"']:
            msg = bot.send_message(message.chat.id, 'Выберите кнопку')
            bot.register_next_step_handler(msg, data)
            return
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Где хотели бы осуществлять волонтёрские работы: " + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Планируемые даты заезда и выезда?', reply_markup=markup)
        bot.register_next_step_handler(msg, language)


def language(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
        
    else:
        if re.match('[\w\s- .,]{' + str(len(message.text)) + '}', message.text) is None:
            msg = bot.send_message(message.chat.id, 'Введите корректные данные о датах заезда и выезда')
            bot.register_next_step_handler(msg, territory)
            return
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Планируемые даты заезда и выезда" + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Владеете ли Вы какими-либо языками? Если да, то какими?')
        bot.register_next_step_handler(msg, experience)


def experience(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
        
    else:
        if re.match('[\w\s- .,]{' + str(len(message.text)) + '}', message.text) is None:
            msg = bot.send_message(message.chat.id, 'Введите корректные данные о языках')
            bot.register_next_step_handler(msg, territory)
            return
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Языки" + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Имеете ли Вы опыт волонтёрских работ?')
        bot.register_next_step_handler(msg, about)


def about(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
        
    else:
        if re.match('[\w\s- .,]{' + str(len(message.text)) + '}', message.text) is None:
            msg = bot.send_message(message.chat.id, 'Введите корректные данные о вашем опыте')
            bot.register_next_step_handler(msg, territory)
            return
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Опыт волонтёрских работ" + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Почему ты хочешь стать волонтёром? Коротко напиши о себе')
        bot.register_next_step_handler(msg, written_down)


def written_down(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
        
    else:
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("О себе" + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Успешно записано!',
                                reply_markup=application)
        bot.register_next_step_handler(msg, application_check)


# Заява на участие:
def fio(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
            
    else:
        if re.match('[а-яА-Я ]{' + str(len(message.text)) + ',' + str(len(message.text)) + '}', message.text) is None:
            msg = bot.send_message(message.chat.id, 'Введите корректное ФИО')
            bot.register_next_step_handler(msg, fio)
            return
        else:
            if not os.path.isdir("users/" + str(message.chat.id)):
                os.mkdir("users/" + str(message.chat.id))
                os.mkdir("users/" + str(message.chat.id) + '/recommendation')
                os.mkdir("users/" + str(message.chat.id) + '/insurance')
                os.mkdir("users/" + str(message.chat.id) + '/contract')
                os.mkdir("users/" + str(message.chat.id) + '/video')
            file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'w')
            file.write("ФИО: " + str(message.text) + '\n')
            msg = bot.send_message(message.chat.id, 'Укажите Вашу электронную почту:')
            bot.register_next_step_handler(msg, email)

def email(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
        
    else:
        if re.match('\w*@\w*\.\w*', message.text) is None:
            msg = bot.send_message(message.chat.id, 'Введите корректный email')
            bot.register_next_step_handler(msg, email)
            return
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Почта: " + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Теперь укажите Вашу дату рождения:')
        bot.register_next_step_handler(msg, phone)


def phone(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
            
    else:
        if re.match('\d{2}\.\d{2}\.\d{4}', message.text) is None:
            msg = bot.send_message(message.chat.id, 'Введите корректную дату')
            bot.register_next_step_handler(msg, phone)
            return
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Дата рождения: " + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Ссылка на страницу в любимой соцсети')
        bot.register_next_step_handler(msg, social_network)


def social_network(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
            
    else:
        if not os.path.isdir("users/" + str(message.chat.id)):
            os.mkdir("users/" + str(message.chat.id))
            os.mkdir("users/" + str(message.chat.id) + '/recommendation')
            os.mkdir("users/" + str(message.chat.id) + '/insurance')
            os.mkdir("users/" + str(message.chat.id) + '/contract')
            os.mkdir("users/" + str(message.chat.id) + '/video')
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Введите социальная сеть: " + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Где ты живёшь (край/область, населённый пункт)?')
        bot.register_next_step_handler(msg, where_live)


def where_live(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
        
    else:
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Населённый пункт: " + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Чем ты занимаешься (сфера деятельности, профессия, направление учёбы)?')
        bot.register_next_step_handler(msg, hobby)


def hobby(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
        
    else:
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Чем занимаюсь: " + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Опиши свой походный опыт')
        bot.register_next_step_handler(msg, hikin_experience)


def hikin_experience(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)

    else:
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Походный опыт: " + str(message.text) + '\n')
        msg = bot.send_message(message.chat.id, 'Какую самую дальнюю точку РФ ты посетил?')
        bot.register_next_step_handler(msg, distant_plase)


def distant_plase(message):
    if message.text == 'Главное меню':
        msg = bot.send_message(message.chat.id,
                               "Главное меню",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
    
    else:
        file = open("users/" + str(message.chat.id) + '/Анкета.txt', 'a')
        file.write("Самая дальняя точка РФ: " + str(message.text) + '\n')
        bot.send_message(message.chat.id, 'Успешно записано!')
        msg = bot.send_message(message.chat.id,
                            '''Заявок всегда в десятки раз больше, чем мест. Мы тщательно отбираем волонтеров, учитываем их образование, профессию, наличие рекомендаций от других заповедников и личные качества. Дистанционно выбрать подходящего человека бывает сложно, поэтому мы рады, когда вы сопровождаете заявки короткими видео о себе (на 1-2 минуты)''',
                            reply_markup=videoKeyboard)
        bot.register_next_step_handler(msg, application_check)


# Кинуть ссылку на видео:
@bot.message_handler(content_types=['video'])
def video_check(message):
    if message.video is None:
        application_check(message)
        return
    try:
        file_info = bot.get_file(message.video.file_id)

        downloaded_file = bot.download_file(file_info.file_path)
        if not os.path.isdir("users/" + str(message.chat.id)):
            os.mkdir("users/" + str(message.chat.id))
            os.mkdir("users/" + str(message.chat.id) + '/recommendation')
            os.mkdir("users/" + str(message.chat.id) + '/insurance')
            os.mkdir("users/" + str(message.chat.id) + '/contract')
            os.mkdir("users/" + str(message.chat.id) + '/video')
        src = 'users/' + str(message.chat.id) + '/video/' + str(file_info.file_path).split('/')[-1]
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, "Успешно сохранено!")
        bot.send_message(message.chat.id, "Отлично, пора переходить к следующему шагу:")
        msg = bot.send_message(message.chat.id,
                               'Если у вас есть рекомендации или благодарности, загрузите их пожалуйста',
                               reply_markup=recommendationKeyboard)
        bot.register_next_step_handler(msg, application_check)
    except Exception as e:
        bot.send_message(message.chat.id,
                         e,
                         reply_markup=videoKeyboard)
        msg = bot.send_message(message.chat.id,
                               'Кажется, что-то пошло не так. Повторите попытку',
                               reply_markup=videoKeyboard)
        bot.register_next_step_handler(msg, video_check)


@bot.message_handler(content_types=['photo'])
def image_check(message):
    if message.photo is None:
        application_check(message)
        return
    try:
        file_info = bot.get_file(message.photo[-1].file_id)

        downloaded_file = bot.download_file(file_info.file_path)

        if not os.path.isdir("users/" + str(message.chat.id)):
            os.mkdir("users/" + str(message.chat.id))
            os.mkdir("users/" + str(message.chat.id) + '/recommendation')
            os.mkdir("users/" + str(message.chat.id) + '/insurance')
            os.mkdir("users/" + str(message.chat.id) + '/contract')
            os.mkdir("users/" + str(message.chat.id) + '/video')
        src = 'users/' + str(message.chat.id) + '/recommendation/' + str(file_info.file_path).split('/')[-1]
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        msg = bot.send_message(message.chat.id,
                               'Успешно сохранено',
                               reply_markup=recommendationKeyboard)
        bot.register_next_step_handler(msg, application_check)
    except Exception as e:
        msg = bot.send_message(message.chat.id,
                               'Кажется, что-то пошло не так. Повторите попытку.\n' + str(e),
                               reply_markup=recommendationKeyboard)
        bot.register_next_step_handler(msg, image_check)


def insurance_check(message):
    if message.photo is None:
        application_check(message)
        return
    try:
        file_info = bot.get_file(message.photo[-1].file_id)

        downloaded_file = bot.download_file(file_info.file_path)

        if not os.path.isdir("users/" + str(message.chat.id)):
            os.mkdir("users/" + str(message.chat.id))
            os.mkdir("users/" + str(message.chat.id) + '/recommendation')
            os.mkdir("users/" + str(message.chat.id) + '/insurance')
            os.mkdir("users/" + str(message.chat.id) + '/contract')
            os.mkdir("users/" + str(message.chat.id) + '/video')
        src = 'users/' + str(message.chat.id) + '/insurance/' + str(file_info.file_path).split('/')[-1]
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        msg = bot.reply_to(message, "Успешно сохранено!")
        bot.register_next_step_handler(msg, )
    except Exception as e:
        msg = bot.send_message(message.chat.id,
                               'Кажется, что-то пошло не так. Повторите попытку',
                               reply_markup=insuranceKeyboard)
        bot.register_next_step_handler(msg, insurance_check)


def contract_check(message):
    if message.photo is None:
        application_check(message)
        return
    try:
        # for i in range(len(message.photo)):
        file_info = bot.get_file(message.photo[-1].file_id)

        downloaded_file = bot.download_file(file_info.file_path)

        if not os.path.isdir("users/" + str(message.chat.id)):
            os.mkdir("users/" + str(message.chat.id))
            os.mkdir("users/" + str(message.chat.id) + '/recommendation')
            os.mkdir("users/" + str(message.chat.id) + '/insurance')
            os.mkdir("users/" + str(message.chat.id) + '/contract')
            os.mkdir("users/" + str(message.chat.id) + '/video')

        src = 'users/' + str(message.chat.id) + '/contract/' + file_info.file_path.split('/')[-1]
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, "Успешно сохранено!")
        msg = bot.send_message(message.chat.id, "Если у Вас остались вопросы - напишите в чат", reply_markup=keyboard)
        bot.register_next_step_handler(msg, keyboard_commands)
    except Exception as e:
        msg = bot.send_message(message.chat.id,
                               'Кажется, что-то пошло не так. Повторите попытку.\n' + str(e),
                               reply_markup=contractKeyboard)
        bot.register_next_step_handler(msg, contract_check)


bot.polling()
