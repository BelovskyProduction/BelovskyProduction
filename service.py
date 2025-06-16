import asyncio
import functools
import os
import logging
import json
from bson import ObjectId

from aiogram import Bot, md
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from openai import AsyncOpenAI, OpenAIError
from pymongo.results import InsertOneResult
from pymongo.synchronous.collection import Collection

import text
from database import get_collection, SURVEYS, STATE_DATA, USERS, EVENT_ORDERS
from datetime import datetime

from keyboard import generate_question_answer_menu, main_menu
from validator import AnswerValidator, AnswerTypes


survey_questions = {
    'Свадьба':
        {1: {'question': 'Как зовут молодоженов?', 'type': AnswerTypes.text},
         2: {'question': 'Сколько лет?', 'type': AnswerTypes.text},
         3: {'question': 'Как познакомились?', 'type': AnswerTypes.large_text},
         4: {'question': 'Какие увлечения/хобби?', 'type': AnswerTypes.large_text},
         5: {'question': 'Любимый цвет?', 'type': AnswerTypes.text},
         6: {'question': 'Любимые исполнители?', 'type': AnswerTypes.text},
         7: {'question': 'Предпочтительный стиль проведения мероприятия?', 'type': AnswerTypes.text},
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

chat_questions = {1: {'question': 'Как тебя зовут?', 'type': AnswerTypes.text},
                  2: {'question': 'Номер телефона для связи?', 'type': AnswerTypes.phone}}

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
    return AsyncOpenAI(api_key=os.getenv('OPEN_AI_TOKEN'), base_url=os.getenv('BASE_AI_URL'), max_retries=0)


def get_prompt(event_type, survey_answers):
    user_content = f"Сгенерируй концепцию для мероприятия типа: '{event_type}' на основе следующих ответов: {survey_answers}. " \
                   f"Ответ должен содержать только следующие пункты: {prompt_details.get(event_type)}. " \
                   f"Значение пунктов должно быть в виде текста"
    prompt = {'model': os.getenv('LLM_MODEL'), 'response_format': {'type': 'json_object'}}
    messages = [{'role': "system", "content": "You are a helpful assistant. You response in JSON format"},
                {'role': 'user', "content": user_content}]
    prompt.update({'messages': messages})
    return prompt


def clean_json_block(json_block: str):
    if json_block.startswith("```") and json_block.endswith("```"):
        return json_block.strip("`")
    return json_block


async def format_conception(conception: str, event_type: str) -> (str, dict):
    try:
        conception = clean_json_block(conception)
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
    try:
        await bot.send_message(chat_id=int(admin_id), text=message)
    except TelegramBadRequest as e:
        logger.warning(f"failed to notify admin: {e.message}")


async def check_if_user_can_start_survey(user_id: ObjectId):
    collection = get_collection(SURVEYS)
    maximum_surveys = int(os.getenv('MAX_SURVEYS_NUMBER'))
    surveys_done_by_user = collection.count_documents({'user_id': user_id})
    return surveys_done_by_user < maximum_surveys


def generate_survey_confirm_text(questions, survey_answers):
    message = 'Результаты опроса:\n\n' + '\n'.join(
        f"*Вопрос*: {question} *Ответ*: {md.quote(survey_answers.get(str(question_number), 'Нет ответа'))}"
        for question_number, question in questions.items()
    )
    return message


def unite_questions_and_answers(questions, answers):
    united_answers = {}
    for question, answer in zip(questions.values(), answers.values()):
        united_answers.update({question: answer})
    return united_answers


async def save_to_db(collection: Collection, data: dict) -> InsertOneResult:
    result = collection.insert_one(data)
    return result


async def save_user_to_db(user_data: dict) -> ObjectId:
    current_date = datetime.now().strftime('%d %b %Y %H:%M:%S')
    collection = get_collection(USERS)
    result = await save_to_db(collection, {**user_data, 'registration_date': current_date})
    return result.inserted_id


async def save_event_order_to_db(user_id: ObjectId, event_type: str):
    current_data = datetime.now().strftime('%d %b %Y %H:%M:%S')
    collection = get_collection(EVENT_ORDERS)
    await save_to_db(collection, {'user_id': user_id, 'event_type': event_type, 'order_date': current_data})


async def save_survey_to_db(user_id: ObjectId, survey_data: dict, questions: dict, event_type: str, conception: dict):
    collection = get_collection(SURVEYS)
    current_date = datetime.now().strftime('%d %b %Y %H:%M:%S')
    answers = unite_questions_and_answers(questions, survey_data)
    data = {'user_id': user_id, 'event_type': event_type, 'answers': answers, 'conception': conception, 'created_at': current_date}
    await save_to_db(collection, data)


def get_survey_questions(event_type: str, without_question_data=False):
    questions = survey_questions.get(event_type, {})
    if without_question_data:
        questions = {q_number: q_data.get('question') for q_number, q_data in questions.items()}
    return questions


def get_next_chat_question(question_number: int):
    question_data = chat_questions.get(question_number, {})
    return question_data.get('question', None)


def get_next_question(event_type: str, question_number: int) -> (str, list | None):
    questions = get_survey_questions(event_type)
    question_data = questions.get(question_number)
    question, variants = question_data.get('question'), question_data.get('variants')
    return question, variants


def get_question_answer_type(question_number: int, event_type: str = None):
    if event_type:
        questions = get_survey_questions(event_type)
    else:
        questions = chat_questions
    question_data = questions.get(question_number)
    return question_data.get('type')


def get_survey_question_number(event_type: str):
    return len(survey_questions.get(event_type, {}))


def get_chat_question_number():
    return len(chat_questions)


async def send_next_question(event_type, question_number, chat_id, bot: Bot):
    keyboard = None
    question, variants = get_next_question(event_type, int(question_number))
    if variants:
        keyboard = generate_question_answer_menu(variants)
    message = await bot.send_message(chat_id=chat_id, text=question, reply_markup=keyboard)
    return message.message_id


async def update_state_for_user_with_pending_generation():
    logger.info('Collecting user ids')
    collection = get_collection(STATE_DATA)
    pending_users = collection.aggregate([
        {'$match': {'state': 'SurveyState:conception_generating'}},
        {'$project': {'_id': 0, 'user_id': '$data.user_id'}},
        {'$group': {'_id': None, 'user_ids': {'$push': '$user_id'}}}
    ]).to_list()
    if pending_users:
        user_ids = pending_users[0].get('user_ids', None)
        logger.info('Updating users state')
        update_result = collection.update_many({'state': 'SurveyState:conception_generating'},
                                               {'$set': {'state': 'SurveyState:ready_to_survey'}})
        logger.info('Updated users: %s', update_result.modified_count)
        return user_ids

    logger.info('Pending users not found')


async def notify_pending_users(user_ids, bot):
    for u_id in user_ids:
        try:
            await bot.send_message(chat_id=u_id, text=text.conception_error, reply_markup=main_menu)
        except Exception:
            pass


async def clear_pending_conception_generation(bot):
    logger.info('Start clearing pending conception generation')
    updated_users = await update_state_for_user_with_pending_generation()
    if updated_users:
        logger.info('Notifying pending users')
        await notify_pending_users(updated_users, bot)
    logger.info('Clearing finished')


async def delete_tg_message(chat_id: int | str, message_id: int, bot: Bot):
    """
    Safely delete tg message
    :param chat_id: telegram chat id
    :param message_id: message id in chat
    :param bot: aiogram bot instance
    :return: None
    """
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except TelegramBadRequest as e:
        logger.warning(f"failed to delete message: {e.message}")


async def validate_answer(chat_id: int, question_number: int | str, answer: str, state: FSMContext, bot: Bot,
                          event_type: str | None = None) -> bool:
    """
    Validates question answer. If answer incorrect notifies user.
    :param chat_id: telegram chat id
    :param question_number: question to which user answers
    :param answer: question answer
    :param state: FSM user state
    :param bot: aiogram bot instance
    :param event_type: type of event
    :return: validation result
    """
    answer_type = get_question_answer_type(int(question_number), event_type)
    validated, error_message = AnswerValidator.validate(answer, answer_type)
    if not validated:
        error_message = await bot.send_message(chat_id=chat_id, text=error_message)
        await state.update_data(message_to_delete=error_message.message_id)
    return validated


async def process_message(message: Message | CallbackQuery, bot: Bot) -> tuple[str, int]:
    """
    Processes user message to receive answer to question. If message type is Aiogram.Message than also deleting it from chat
    :param message: User message
    :param bot: Aiogram bot instance
    :return: chat id and answer
    """
    if isinstance(message, Message):
        answer = message.text
        chat_id = message.chat.id
        await delete_tg_message(chat_id=chat_id, message_id=message.message_id, bot=bot)
    else:
        answer = message.data.split('_')[-1]
        chat_id = message.message.chat.id
    return answer, chat_id
