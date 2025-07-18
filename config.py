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
        {1: {'question': 'Имена жениха и невесты?', 'type': AnswerTypes.text},
         2: {'question': 'Какие увлечения и хобби?', 'type': AnswerTypes.text},
         3: {'question': 'Формат свадьбы(классическая, выездная, тематическая, мини-свадьба и т.д.)',
             'type': AnswerTypes.text},
         4: {'question': 'Предпочтительный тип площадки(ресторан, загородный клуб, банкетный зал, природа и т.д.)',
             'type': AnswerTypes.text},
         5: {'question': 'Есть ли выбранная цветовая гамма или тематика или любимый цвет?', 'type': AnswerTypes.text},
         6: {'question': 'Любимый исполнитель или музыкальный стиль?', 'type': AnswerTypes.text},
         7: {'question': 'Какие элементы декора важны?(флористика, фотозона, освещение, текстиль и т.д.)',
             'type': AnswerTypes.text},
         8: {'question': 'Какие ключевые моменты должны быть?(выкуп, церемония, фуршет, банкет, первый танец и т.д.)',
             'type': AnswerTypes.text},
         9: {'question': 'Есть ли семейные традиции, которые нужно учесть?', 'type': AnswerTypes.text},
         10: {'question': 'Какие моменты для вас самые важные?', 'type': AnswerTypes.text}},
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
