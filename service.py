import os

from aiogram import Bot

from database import get_collection, SURVEYS
from datetime import datetime


survey_questions = {
    'Cвадьба':
        {1: 'Как зовут молодоженов?', 2: 'Сколько лет?', 3: 'Как познакомились?',
         4: 'Какие увлечения/хобби?', 5: 'Любимый цвет?', 6: 'Любимые исполнители?',
         7: 'Предпочтительный стиль проведения мероприятия?', 8: 'Любимое время года?',
         9: 'Любимая марка авто?'},
    'День рождения':
        {1: 'Как зовут именинника?', 2: 'Cколько исполняется лет?', 3: 'Любимый цвет?', 4: 'Сфера деятельности?',
         5: 'Любимое хобби?', 6: 'Любимый исполнитель?'},
    'Корпоратив':
        {1: 'Название компании?', 2: 'Сфера деятельности?', 3: 'Количество сотрудников?', 4: 'Формат Корпоратива?',
         5: 'Тематический или деловой корпоратив?'},
    'Конференция':
        {1: 'Название компании?', 2: 'Тема конференции?', 3: 'Количество человек?'}
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


def get_survey_questions(event_type: str):
    return survey_questions.get(event_type, {})


def get_next_question(event_type: str, question_number: int):
    questions = get_survey_questions(event_type)
    return questions.get(question_number)


def get_survey_question_number(event_type: str):
    return len(survey_questions.get(event_type, {}))
