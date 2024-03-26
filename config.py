import os
from dotenv import load_dotenv
import logging

GENRES = ['Хоррор', 'Фэнтези', 'Детектив']
CHARACTERS = ['Андроид Коннор', 'Шерлок Холмс', 'Гермиона Грейнджер', 'Лиса Алиса']
SETTINGS = ['Замок', 'Лес', 'Город']

load_dotenv()
TOKEN = os.getenv('TG_TOKEN')

user_data = {}

MAX_SYMBOLS = 50
MAX_SESSIONS = 2
MAX_TOKENS_IN_SESSION = 1500

TEMPERATURE = 1.2
MAX_TOKENS = 150

IAM_TOKEN = ''
FOLDER_ID = ''

URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
HEADERS = {
    'Authorization': f'Bearer {IAM_TOKEN}',
    'Content-Type': 'application/json'
}

SYSTEM_PROMPT = ("Ты пишешь историю вместе с человеком. "
                 "Историю вы пишете по очереди. Начинает человек, а ты продолжаешь. "
                 "Если это уместно, ты можешь добавлять в историю диалог между персонажами. "
                 "Диалоги пиши с новой строки и отделяй тире. "
                 "Не пиши никакого пояснительного текста в начале, а просто логично продолжай историю."
                 )

CONTINUE_STORY = 'Продолжи сюжет в 1-3 предложения и оставь интригу. Не пиши никакой пояснительный текст от себя'
END_STORY = 'Напиши завершение истории c неожиданной развязкой. Не пиши никакой пояснительный текст от себя'

logging.basicConfig(level=logging.DEBUG, filename='logs.log')
logger = logging.getLogger(__name__)