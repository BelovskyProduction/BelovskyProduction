import functools
import logging
import os

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from openai import AsyncOpenAI

logger = logging.getLogger()


@functools.lru_cache(maxsize=1)
def get_open_ai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=os.getenv('OPEN_AI_TOKEN'), base_url=os.getenv('BASE_AI_URL'), max_retries=0)


def format_message(message: str, **kwargs):
    return message.format(**kwargs)


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


def unite_questions_and_answers(questions, answers):
    united_answers = {}
    for question, answer in zip(questions.values(), answers.values()):
        united_answers.update({question: answer})
    return united_answers
