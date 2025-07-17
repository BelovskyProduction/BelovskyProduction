import os

from dotenv import load_dotenv
from validator import AnswerTypes

load_dotenv()

# TG bot settings
BOT_TOKEN = os.getenv('BOT_TOKEN')

# database settings
MONGO_URL = os.getenv('MONGO_URL')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')


# registration questions
REGISTRATION_QUESTIONS = {1: {'question': 'Как тебя зовут?', 'type': AnswerTypes.text},
                          2: {'question': 'Номер телефона для связи?', 'type': AnswerTypes.phone}}

# survey questions
SURVEY_QUESTIONS = {
    'Свадьба':
        {1: {'question': 'Как зовут молодоженов?', 'type': AnswerTypes.text},
         2: {'question': 'Сколько лет?', 'type': AnswerTypes.text},
         3: {'question': 'Как познакомились?', 'type': AnswerTypes.large_text},
         4: {'question': 'Какие увлечения/хобби?', 'type': AnswerTypes.large_text},
         5: {'question': 'Любимый цвет?', 'type': AnswerTypes.text},
         6: {'question': 'Любимые исполнители?', 'type': AnswerTypes.text},
         7: {'question': 'Предпочтительный стиль мероприятия(оформление)?', 'type': AnswerTypes.text},
         8: {'question': 'Любимое время года?', 'type': AnswerTypes.text},
         9: {'question': 'Любимая марка авто?', 'type': AnswerTypes.text}},
    'День рождения':
        {1: {'question': 'Как зовут именинника?', 'type': AnswerTypes.text},
         2: {'question': 'Cколько исполняется лет?', 'type': AnswerTypes.age},
         3: {'question': 'Любимый цвет?', 'type': AnswerTypes.text},
         4: {'question': 'Сфера деятельности?', 'type': AnswerTypes.text},
         5: {'question': 'Любимое хобби?', 'type': AnswerTypes.text},
         6: {'question': 'Любимый исполнитель?', 'type': AnswerTypes.text}},
    'Корпоратив':
        {1: {'question': 'Название компании?', 'type': AnswerTypes.text},
         2: {'question': 'Сфера деятельности?', 'type': AnswerTypes.text},
         3: {'question': 'Количество сотрудников?', 'type': AnswerTypes.number},
         4: {'question': 'Формат Корпоратива?', 'type': AnswerTypes.text,
             'variants': ['Отдых на природе', 'Ресторан и шоу программа']},
         5: {'question': 'Тематический или деловой корпоратив?', 'type': AnswerTypes.text,
             'variants': ['Тематический', 'Деловой']}},
    'Конференция':
        {1: {'question': 'Название конференции?', 'type': AnswerTypes.text},
         2: {'question': 'Тема конференции?', 'type': AnswerTypes.text},
         3: {'question': 'Количество компаний учавствующих в конференции?', 'type': AnswerTypes.number},
         4: {'question': 'Место проведения?', 'type': AnswerTypes.text},
         5: {'question': 'Время проведения(месяц)?', 'type': AnswerTypes.text},
         6: {'question': 'Цель конференции?', 'type': AnswerTypes.text}}
}
