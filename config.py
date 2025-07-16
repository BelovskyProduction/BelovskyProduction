import os

from dotenv import load_dotenv
from validator import AnswerTypes

load_dotenv()

# TG bot settings
BOT_TOKEN = os.getenv('BOT_TOKEN')

# database settings
MONGO_URL = os.getenv('MONGO_URL')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')


#registration questions
REGISTRATION_QUESTIONS = {1: {'question': 'Как тебя зовут?', 'type': AnswerTypes.text},
                          2: {'question': 'Номер телефона для связи?', 'type': AnswerTypes.phone}}
