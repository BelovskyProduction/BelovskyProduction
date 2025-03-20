import asyncio
import functools
import os
import logging
import json

from aiogram import Bot, md
from openai import AsyncOpenAI, OpenAIError

import text
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

prompt_details = {'Конференция': ['Название конференции', 'Целевая аудитория',
                                  'Программа мероприятия', 'Дополнительные элементы', 'Маркетинг и продвижение',
                                  'Ожидаемые результаты'],
                  'Корпоратив': ['Название мероприятия', 'Цель мероприятия', 'Тематика',
                                 'Программа мероприятия', 'Дополнительные элементы'],
                  'День рождения': ['Тема мероприятия', 'Место', 'Оформление', 'Угощения', 'Программа мероприятия',
                                    'Подарки'],
                  'Свадьба': ['Общая идея', 'Тематика и атмосфера', 'Декор', 'Свадебный торт', 'Место проведения',
                              'Программа', 'Кулинарное меню', 'Дресс-код']}


logger = logging.getLogger()


@functools.lru_cache(maxsize=1)
def get_open_ai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=os.getenv('OPEN_AI_TOKEN'), max_retries=0)


def get_prompt(event_type, survey_answers):
    user_content = f"Сгенерируй концепцию для мероприятия типа: '{event_type}' на основе следующих ответов: {survey_answers}. " \
                   f"Ответ должен содержать только следующие пункты: {prompt_details.get(event_type)}. " \
                   f"Значение пунктов должно быть в виде текста"
    prompt = {'model': os.getenv('LLM_MODEL'), 'response_format': {'type': 'json_object'}}
    messages = [{'role': "system", "content": "You are a helpful assistant. You response in JSON format"},
                {'role': 'user', "content": user_content}]
    prompt.update({'messages': messages})
    return prompt


async def format_conception(conception: str, event_type: str) -> (str, dict):
    try:
        json_conception = json.loads(conception)
        user_conception_keys = prompt_details.get(event_type)[0:4]
        user_conception_format = text.conception_message + ''.join(f'\n\n\t *{key}*: {json_conception.get(key, None)}'
                                                                   for key in user_conception_keys)
        return user_conception_format, json_conception

    except json.JSONDecodeError as e:
        logger.error('Conception format error: %s', e.args)
        return conception, conception
    except Exception as e:
        logger.error('Conception format error: %s', e.args)
        return conception, conception


async def get_event_conception(event_type, survey_answers, retries):
    delay_in_seconds = int(os.getenv('RETRY_DELAY_MINUTES', 2)) * 60
    while retries > 0:
        try:
            return await generate_event_conception(event_type, survey_answers)
        except OpenAIError as e:
            logger.error('Conception generation error: %s', e.args)
            await asyncio.sleep(delay_in_seconds)
            retries -= 1


async def generate_event_conception(event_type, survey_answers):
    gpt_client = get_open_ai_client()
    prompt = get_prompt(event_type, survey_answers)
    completion = await gpt_client.chat.completions.create(**prompt)
    return completion.choices[0].message.content


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
        f"*Вопрос*: {question} *Ответ*: {md.quote(survey_answers.get(question_number, 'Нет ответа'))}"
        for question_number, question in questions.items()
    )
    return message


async def save_survey_to_db(user_id, survey_data, questions, user_data, conception):
    collection = get_collection(SURVEYS)
    current_date = datetime.now().strftime('%d %b %Y %H:%M:%S')
    answers = {}
    for question, answer in zip(questions.values(), survey_data.values()):
        answers.update({question: answer})
    data = {'user_id': user_id, **user_data, 'answers': answers, 'conception': conception, 'created_at': current_date}
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


