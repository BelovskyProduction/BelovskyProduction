from aiogram import Bot
from aiogram.fsm.context import FSMContext

from config import ADVERTISING_QUESTIONS
from keyboard import generate_question_answer_menu
from validator import AnswerValidator


def get_advertising_survey_question_number():
    # TODO: unite with similar method from service

    return len(ADVERTISING_QUESTIONS)


def get_next_question(question_number: int) -> (str, list | None):
    # TODO: unite with similar method from service

    question_data = ADVERTISING_QUESTIONS.get(question_number)
    question, clarification, variants = question_data.get('question'), question_data.get('clarification'), \
        question_data.get('variants')
    return question, clarification, variants


async def send_next_question(question_number, chat_id, bot: Bot):
    # TODO: unite with similar method from service

    keyboard = None
    question, clarification, variants = get_next_question(int(question_number))
    if variants:
        keyboard = generate_question_answer_menu(variants)
    if clarification:
        question += f'({clarification})'
    message = await bot.send_message(chat_id=chat_id, text=question, reply_markup=keyboard)
    return message.message_id


async def validate_answer(chat_id: int, question_number: int | str, answer: str, state: FSMContext, bot: Bot) -> bool:
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
    # TODO: unite with similar method from service
    answer_type = ADVERTISING_QUESTIONS.get(int(question_number)).get('type')
    validated, error_message = AnswerValidator.validate(answer, answer_type)
    if not validated:
        error_message = await bot.send_message(chat_id=chat_id, text=error_message)
        await state.update_data(message_to_delete=error_message.message_id)
    return validated


def get_survey_questions(without_question_data=False):
    # TODO: unite with similar method from service
    questions = ADVERTISING_QUESTIONS.copy()
    if without_question_data:
        questions = {q_number: q_data.get('question') for q_number, q_data in questions.items()}
    return questions
