import telebot
from telebot.types import ReplyKeyboardMarkup
from config import GENRES, CHARACTERS, SETTINGS, TOKEN, user_data, MAX_SYMBOLS, MAX_SESSIONS, CONTINUE_STORY, END_STORY, logger
from gpt import ask_gpt

bot = telebot.TeleBot(TOKEN)


def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for button in buttons_list:
        keyboard.add(button)
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Я - GPT-бот-сценарист.\n'
                                      'Введи команду /make_story для создания истории, а после команды /begin я начну ее!\n'
                                      'Вводи по одному предложению для продолжения истории и закончи ее командой /end !'
                     )
    if not user_data.get(message.chat.id):
        user_data[message.chat.id] = {}
        user_data[message.chat.id]['current_session'] = 0


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, '/start - Запуск бота\n'
                                      '/help - Просмотр команд\n'
                                      '/make_story - Выбрать параметры истории\n'
                                      '/begin - Начать историю\n'
                                      '/end - Закончить историю\n')


@bot.message_handler(commands=['make_story'])
def genre_handler(message):
    user_data[message.chat.id]['current_session'] += 1
    if user_data[message.chat.id]['current_session'] > MAX_SESSIONS:
        bot.send_message(message.chat.id, 'Количество созданных историй достигло максимума!')
        return
    keyboard = create_keyboard(GENRES)
    bot.send_message(message.chat.id, 'Выберите жанр:', reply_markup=keyboard)
    bot.register_next_step_handler(message, save_genre)


def save_genre(message):
    if message.text not in GENRES:
        logger.debug(f'"{message.text}" not found in GENRES')
        bot.send_message(message.chat.id, 'Используйте кнопки для ответа!')
        bot.register_next_step_handler(message, save_genre)
        return

    user_data[message.chat.id]['genre'] = message.text

    keyboard = create_keyboard(CHARACTERS)
    bot.send_message(message.chat.id, 'Ок, теперь выберите персонажа', reply_markup=keyboard)
    bot.register_next_step_handler(message, save_character)


def save_character(message):
    if message.text not in CHARACTERS:
        logger.debug(f'"{message.text}" not found in CHARACTERS')
        bot.send_message(message.chat.id, 'Используйте кнопки для ответа!')
        bot.register_next_step_handler(message, save_character)
        return

    user_data[message.chat.id]['character'] = message.text

    keyboard = create_keyboard(SETTINGS)
    bot.send_message(message.chat.id, 'Выберите сеттинг', reply_markup=keyboard)
    bot.register_next_step_handler(message, save_setting)


def save_setting(message):
    if message.text not in SETTINGS:
        logger.debug(f'"{message.text}" not found in SETTINGS')
        bot.send_message(message.chat.id, 'Используйте кнопки для ответа!')
        bot.register_next_step_handler(message, save_setting)
        return

    user_data[message.chat.id]['setting'] = message.text

    bot.send_message(message.chat.id,
                     'Теперь Вы можете добавить уточняющие факторы и другую информацию в историю по желанию.\n'
                     'Если хотите пропустить этот шаг, введите команду /begin')
    bot.register_next_step_handler(message, save_addition)


def save_addition(message):
    if message.content_type != 'text':
        logger.debug('message must be a text')
        bot.send_message(message.chat.id, 'Введите текстовое сообщение!')
        bot.register_next_step_handler(message, save_addition)
        return
    if len(message.text) > MAX_SYMBOLS:
        bot.send_message(message.chat.id, 'Больше 50 букв не перевариваю')
        bot.register_next_step_handler(message, save_addition)
        return

    user_data[message.chat.id]['addition'] = message.text
    bot.send_message(message.chat.id, 'Отлично! Теперь вводи команду /begin для написания истории')


@bot.message_handler(commands=['begin'])
def begin_story(message):
    if not user_data[message.chat.id]['genre']:
        bot.send_message(message.chat.id, 'Сначала введи команду /make_story !')
        return
    if user_data[message.chat.id]['current_session'] > MAX_SESSIONS:
        bot.send_message(message.chat.id, 'Количество созданных историй достигло максимума!')
        return

    prompt = (f"\nНапиши начало истории в стиле {user_data[message.chat.id]['genre']} "
              f"с главным героем {user_data[message.chat.id]['character']}. "
              f"Вот начальный сеттинг: \n{user_data[message.chat.id]['setting']}. \n"
              "Начало должно быть коротким, 1-3 предложения.\n")

    if user_data[message.chat.id].get('addition'):
        prompt += (f"Также пользователь попросил учесть "
                   f"следующую дополнительную информацию: {user_data[message.chat.id]['additional_info']} ")

    prompt += 'Не пиши никакие подсказки пользователю, что делать дальше. Он сам знает'

    story = ''

    answer = ask_gpt(message.chat.id, prompt, story)
    bot.send_message(message.chat.id, answer)


@bot.message_handler(content_types=['text'])
def continue_story(message):
    if not user_data[message.chat.id].get('messages'):
        bot.send_message(message.chat.id, 'Чтобы продолжить историю, ее нужно начать!\n'
                                          'Введи команду /make_story')
        return

    prompt = CONTINUE_STORY
    story = user_data[message.chat.id]['messages'][2]['text'] + message.text

    answer = ask_gpt(message.chat.id, prompt, story)
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['end'])
def end_story(message):
    if not user_data[message.chat.id].get('messages'):
        bot.send_message(message.chat.id, 'Чтобы закончить историю, ее нужно начать!\n'
                                          'Введи команду /make_story')
        return

    prompt = END_STORY
    story = user_data[message.chat.id]['messages'][2]['text'] + message.text

    answer = ask_gpt(message.chat.id, prompt, story)
    bot.send_message(message.chat.id, answer)


bot.polling()
