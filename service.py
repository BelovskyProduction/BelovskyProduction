import os

from database import get_collection, SURVEYS
from datetime import datetime


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
