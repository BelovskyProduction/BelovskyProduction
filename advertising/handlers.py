import os

from aiogram import Bot
from aiogram.dispatcher.router import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import F

import text
from llm.prompt_builders import AdvertisingPromptBuilder
from llm.service import get_conception
from user_states import AdvertisingStates, SurveyState
from utils import process_message, delete_tg_message, unite_questions_and_answers

from .service import send_next_question, validate_answer, get_advertising_survey_question_number, get_survey_questions, \
    save_advertising_survey_to_db

advertising_router = Router(name='advertising_router')


@advertising_router.message(F.text == f'{chr(0x1F4E2)} Реклама')
async def start_advertising_survey_handler(msg: Message, state: FSMContext, bot: Bot):
    await msg.delete()
    current_state = await state.get_state()

    if current_state in [SurveyState.ready_to_survey.state]:
        chat_id = msg.chat.id
        data = await state.get_data()
        # if data.get('advertise_survey_passed'):
        #     return await msg.answer(text=text.advertising_survey_already_passed)

        await state.set_state(AdvertisingStates.advertising_survey_started)
        starting_question_number = 1
        question_message_id = await send_next_question(question_number=starting_question_number,
                                                       chat_id=chat_id, bot=bot)
        await state.update_data(last_question_number=starting_question_number, message_to_delete=question_message_id,
                                advertising_survey_answers={})


@advertising_router.callback_query(StateFilter(AdvertisingStates.advertising_survey_started), F.data.startswith('answer_'))
@advertising_router.message(StateFilter(AdvertisingStates.advertising_survey_started))
async def survey_question_answer_handler(msg: Message | CallbackQuery, state: FSMContext, bot: Bot):
    answer, chat_id = await process_message(message=msg, bot=bot)
    state_data = await state.get_data()
    if 'message_to_delete' in state_data:
        message_id = state_data.pop('message_to_delete')
        await delete_tg_message(chat_id=chat_id, message_id=message_id, bot=bot)
    current_question_number, survey_answers = state_data.get('last_question_number'), \
        state_data.get('advertising_survey_answers')
    if not await validate_answer(chat_id=chat_id, question_number=current_question_number, answer=answer,
                                 state=state, bot=bot):
        return None
    survey_answers.update({str(current_question_number): answer})

    if current_question_number != get_advertising_survey_question_number():
        current_question_number += 1
        question_message_id = await send_next_question(question_number=current_question_number,
                                                       chat_id=chat_id, bot=bot)
        await state.update_data(last_question_number=current_question_number, advertising_survey_answers=survey_answers,
                                message_to_delete=question_message_id)
    else:
        await state.update_data(advertising_survey_answers=survey_answers, advertise_survey_passed=True)
        await state.set_state(SurveyState.ready_to_survey)
        await bot.send_message(chat_id=chat_id, text=text.advertising_survey_passed)
        questions = get_survey_questions(without_question_data=True)
        united_answers = unite_questions_and_answers(questions, survey_answers)
        prompt_builder = AdvertisingPromptBuilder()
        conception = await get_conception(prompt_builder, united_answers, int(os.getenv('MAX_RETRIES', 2)))
        await save_advertising_survey_to_db(state_data.get('user_id'), united_answers, conception)
