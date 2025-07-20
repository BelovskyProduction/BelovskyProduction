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

ADVERTISING_QUESTIONS = {
    1: {'question': 'Название компании/бренда', 'type': AnswerTypes.text},
    2: {'question': 'Сфера деятельности?',
        'clarification': 'чем занимаетесь, какие товары/услуги предлагаете', 'type': AnswerTypes.large_text},
    3: {'question': 'Каковы основные уникальные торговые предложения(УТП) вашего продукта/услуги?',
        'type': AnswerTypes.large_text},
    4: {'question': 'Есть ли у вас фирменный стиль?', 'clarification': 'логотип, цвета, шрифты, слоганы',
        'type': AnswerTypes.text},
    5: {'question': 'Какова основная цель рекламы?',
        'clarification': 'увеличение продаж, повышение узнаваемости бренда, привлечение трафика, '
                         'продвижение конкретного товара/услуги и т.д.', 'type': AnswerTypes.text},
    6: {'question': 'Какие рекламные каналы вас интересуют?',
        'clarification': 'соцсети, контекстная реклама, таргетированная реклама, баннеры, ТВ, радио, '
                         'наружная реклама и т.д.', 'type': AnswerTypes.text},
    7: {'question': 'Кто ваша целевая аудитория?',
        'clarification': 'пол, возраст, география, доход, интересы, профессия и т.д.', 'type': AnswerTypes.large_text},
    8: {'question': 'Какие боли/потребности вашей ЦА решает ваш продукт/услуга?', 'type': AnswerTypes.large_text},
    9: {'question': 'Где ваша ЦА проводит время онлайн/оффлайн?', 'type': AnswerTypes.large_text},
    10: {'question': 'Какой бюджет вы готовы выделить на рекламу?', 'type': AnswerTypes.text},
    11: {'question': 'На какой срок планируется рекламная кампания?', 'type': AnswerTypes.text},
    12: {'question': 'Есть ли сезонность или особые даты, на которые нужно сделать акцент?', 'type': AnswerTypes.text},
    13: {'question': 'Кто ваши основные конкуренты?', 'type': AnswerTypes.large_text},
    14: {'question': 'Есть ли у вас примеры рекламы конкурентов, которая вам нравится/не нравится?',
        'type': AnswerTypes.large_text},
    15: {'question': 'Какие ключевые преимущества выделяют вас на фоне конкурентов?', 'type': AnswerTypes.large_text},
    16: {'question': 'Есть ли у вас готовые материалы для работы?', 'clarification': 'фото, видео, тексты',
        'type': AnswerTypes.text},
    17: {'question': 'Предпочитаемый стиль коммуникации?',
        'clarification': 'строгий, дружелюбный, юмористический, экспертный и т.д.', 'type': AnswerTypes.text},
    18: {'question': 'Есть ли ограничения по подаче?',
        'clarification': 'например, нельзя использовать определенные цвета, образы', 'type': AnswerTypes.large_text},
    19: {'question': 'Был ли у вас опыт запуска рекламы ранее? Какие результаты?', 'type': AnswerTypes.large_text},
    20: {'question': 'Какие ошибки или проблемы вы хотели бы избежать в новой кампании?', 'type': AnswerTypes.large_text},
    21: {'question': 'Есть ли дополнительные требования или пожелания?', 'type': AnswerTypes.large_text},
}

# prompt config
CONCEPTION_CONTENT = {'Конференция': ['Название конференции', 'Целевая аудитория', 'Программа мероприятия',
                                      'Дополнительные элементы', 'Маркетинг и продвижение', 'Ожидаемые результаты'],
                      'Корпоратив': ['Название мероприятия', 'Цель мероприятия', 'Тематика',
                                     'Программа мероприятия', 'Дополнительные элементы'],
                      'День рождения': ['Тема мероприятия', 'Место', 'Оформление', 'Угощения', 'Программа мероприятия',
                                        'Подарки'],
                      'Свадьба': ['Общая идея', 'Тематика и атмосфера', 'Декор', 'Свадебный торт', 'Место проведения',
                                  'Программа', 'Кулинарное меню', 'Дресс-код', 'Приглашение', 'Задачи ведущего']}
