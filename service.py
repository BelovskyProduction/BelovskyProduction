import os

from aiogram import Bot

from database import get_collection, SURVEYS
from datetime import datetime

from keyboard import generate_question_answer_menu

survey_questions = {
    'Cвадьба':
        {1: {'question': 'Как зовут молодоженов?'}, 2: {'question': 'Сколько лет?'},
         3: {'question': 'Как познакомились?'},
         4: {'question': 'Какие увлечения/хобби?'}, 5: {'question': 'Любимый цвет?'},
         6: {'question': 'Любимые исполнители?'},
         7: {'question': 'Предпочтительный стиль проведения мероприятия?'},
         8: {'question': 'Любимое время года?'},
         9: {'question': 'Любимая марка авто?'}},
    'День рождения':
        {1: {'question': 'Как зовут именинника?'}, 2: {'question': 'Cколько исполняется лет?'},
         3: {'question': 'Любимый цвет?'}, 4: {'question': 'Сфера деятельности?'},
         5: {'question': 'Любимое хобби?'}, 6: {'question': 'Любимый исполнитель?'}},
    'Корпоратив':
        {1: {'question': 'Название компании?'}, 2: {'question': 'Сфера деятельности?'},
         3: {'question': 'Количество сотрудников?'}, 4: {'question': 'Формат Корпоратива?',
                                                         'variants': ['Отдых на природе', 'Ресторан и шоу программа']},
         5: {'question': 'Тематический или деловой корпоратив?', 'variants': ['Тематический', 'Деловой']}},
    'Конференция':
        {1: {'question': 'Название компании?'}, 2: {'question': 'Тема конференции?'},
         3: {'question': 'Количество человек?'}}
}


async def notify_admin_about_new_client(user_data, bot: Bot):
    admin_id = os.getenv('ADMIN_ID')
    message = f'У вас новый клиент! \n'
    for key, value in user_data.items():
        message += f'{key}: {value} \n'
    await bot.send_message(chat_id=int(admin_id), text=message)


async def check_if_user_can_start_survey(user_id: int):
    collection = get_collection(SURVEYS)
    maximum_surveys = int(os.getenv('MAX_SURVEYS_NUMBER'))
    surveys_done_by_user = collection.count_documents({'user_id': user_id})
    return surveys_done_by_user < maximum_surveys


def generate_survey_confirm_text(questions, survey_answers):
    message = 'Результаты опроса:\n\n' + '\n'.join(
        f"*Вопрос*: {question} *Ответ*: {survey_answers.get(question_number, 'Нет ответа')}"
        for question_number, question in questions.items()
    )
    return message


async def save_survey_to_db(user_id, survey_data, questions, user_data):
    collection = get_collection(SURVEYS)
    current_date = datetime.now().strftime('%d %b %Y %H:%M:%S')
    answers = {}
    for question, answer in zip(questions.values(), survey_data.values()):
        answers.update({question: answer})
    data = {'user_id': user_id, **user_data, 'answers': answers, 'created_at': current_date}
    collection.insert_one(data)


def get_survey_questions(event_type: str, without_question_data=False):
    questions = survey_questions.get(event_type, {})
    if without_question_data:
        questions = {q_number: q_data.get('question') for q_number, q_data in questions.items()}
    return questions


def get_next_question(event_type: str, question_number: int) -> (str, list | None):
    questions = get_survey_questions(event_type)
    question_data = questions.get(question_number)
    question, variants = question_data.get('question'), question_data.get('variants')
    return question, variants


def get_survey_question_number(event_type: str):
    return len(survey_questions.get(event_type, {}))


async def send_next_question(event_type, question_number, chat_id, bot: Bot):
    keyboard = None
    question, variants = get_next_question(event_type, int(question_number))
    if variants:
        keyboard = generate_question_answer_menu(variants)
    message = await bot.send_message(chat_id=chat_id, text=question, reply_markup=keyboard)
    return message.message_id


