import os

from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import F
from pymongo.errors import PyMongoError

import text
from keyboard import main_menu, survey_confirm_menu, generate_survey_edit_menu, generate_event_type_menu,\
    survey_request_menu
from service import save_survey_to_db, generate_survey_confirm_text, check_if_user_can_start_survey, \
    notify_admin_about_new_client, get_survey_question_number, get_survey_questions, \
    send_next_question, get_event_conception, format_conception, get_next_user_registration_question, \
    get_user_registration_questions_number, unite_questions_and_answers, delete_tg_message, validate_answer, process_message, \
    save_user_to_db, save_event_order_to_db
from utils import format_message
from user_states import SurveyState

router = Router(name='conception_router')

event_types = ['Свадьба', 'День рождения', 'Корпоратив', 'Конференция', 'Другое']

user_data_map = {1: 'Имя', 2: 'Номер телефона'}

#TODO: add handling when usere type text answer instead of click answer button, when user editing he can press edit button


@router.message(Command('start'))
async def start_handler(msg: Message, state: FSMContext):
    current_state = await state.get_state()

    if not current_state:
        question_number = 1
        message = format_message(text.welcome_message, username=msg.from_user.username)
        await state.set_state(SurveyState.chat_started)
        await msg.answer(text=message, reply_markup=ReplyKeyboardRemove())
        question = get_next_user_registration_question(question_number)
        send_question = await msg.answer(text=question)
        await state.update_data(last_question_number=question_number, user_data={},
                                message_to_delete=send_question.message_id)


@router.message(StateFilter(SurveyState.chat_started.state))
async def registration_question_answer_handler(msg: Message, state: FSMContext, bot: Bot):
    answer = msg.text
    state_data = await state.get_data()
    await msg.delete()
    if 'message_to_delete' in state_data:
        message_id = state_data.pop('message_to_delete')
        await delete_tg_message(chat_id=msg.chat.id, message_id=message_id, bot=bot)
    current_question_number, user_data = state_data.get('last_question_number'), state_data.get('user_data')
    if not await validate_answer(chat_id=msg.chat.id, question_number=current_question_number, answer=answer,
                                 state=state, bot=bot):
        return None
    user_data.update({user_data_map.get(current_question_number): answer})
    await state.update_data(user_data=user_data)

    if current_question_number != get_user_registration_questions_number():
        current_question_number += 1
        question = get_next_user_registration_question(current_question_number)
        send_question = await msg.answer(text=question)
        await state.update_data(last_question_number=current_question_number,
                                message_to_delete=send_question.message_id)
    else:
        try:
            user_id = await save_user_to_db({'telegram_id': msg.from_user.id, **user_data})
            await state.update_data(user_id=user_id)
            await state.set_state(SurveyState.choosing_event_type_for_order)
            menu = generate_event_type_menu(event_types)
            await msg.answer(text=text.event_choose_message, reply_markup=menu.as_markup(), parse_mode='Markdown')
        except PyMongoError:
            await msg.answer(text=text.answer_default_message)


@router.callback_query(StateFilter(SurveyState.choosing_event_type_for_order), F.data.startswith('event_'))
async def order_event_type_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

    event_type = callback.data.split('_')[-1]
    state_data = await state.get_data()
    try:
        await save_event_order_to_db(state_data.get('user_id'), event_type)
    except PyMongoError:
        menu = generate_event_type_menu(event_types)
        return await bot.send_message(chat_id=callback.message.chat.id, text=text.answer_default_message,
                                      reply_markup=menu.as_markup())

    user_data = state_data.get('user_data')
    #TODO: remove meropriyatie
    user_data.update({'Мероприятие': event_type})
    await state.update_data(user_data=user_data, event_type=event_type)
    await notify_admin_about_new_client(user_data, bot)

    if event_type.lower() == 'другое':
        await state.set_state(SurveyState.ready_to_survey)
        await bot.send_message(chat_id=callback.message.chat.id, text=text.other_event_reply, reply_markup=main_menu)
    else:
        await state.set_state(SurveyState.deciding_whether_to_generate_conception)
        await bot.send_message(chat_id=callback.message.chat.id, text=text.event_survey_start_question,
                               reply_markup=survey_request_menu)


@router.callback_query(StateFilter(SurveyState.deciding_whether_to_generate_conception), F.data.startswith('surveyrequest'))
async def survey_request_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.delete()
    want_to_start_survey = callback.data.split('_')[-1]
    chat_id = callback.message.chat.id
    if want_to_start_survey == 'yes':
        question_number = 1
        state_data = await state.get_data()
        event_type = state_data.get('event_type')

        start_text = text.survey_start_text.get(event_type, text.user_want_survey)
        await bot.send_message(chat_id=callback.message.chat.id, text=start_text)
        await state.set_state(SurveyState.survey_started.state)
        question_message_id = await send_next_question(event_type=event_type, question_number=question_number,
                                                       chat_id=chat_id, bot=bot)
        await state.update_data(last_question_number=question_number, survey_answers={},
                                message_to_delete=question_message_id)
    else:
        await state.set_state(SurveyState.ready_to_survey)
        await bot.send_message(chat_id=chat_id, text=text.user_dont_want_survey, reply_markup=main_menu)


@router.message(F.text == f'{chr(0x1F4CB)} Опрос')
async def start_survey_handler(msg: Message, state: FSMContext, bot: Bot):
    await msg.delete()
    current_state = await state.get_state()

    if current_state in [SurveyState.ready_to_survey.state]:
        data = await state.get_data()
        if not await check_if_user_can_start_survey(data.get('user_id')):
            return await msg.answer(text=text.surveys_limit_reached)

        await state.set_state(SurveyState.survey_started)
        events = [event for event in event_types if event != 'Другое']
        menu = generate_event_type_menu(events)
        await msg.answer(text=text.event_choose_message, reply_markup=menu.as_markup(), parse_mode='Markdown')


@router.callback_query(StateFilter(SurveyState.survey_started), F.data.startswith('event_'))
async def survey_event_type_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

    event_type = callback.data.split('_')[-1]
    question_number = 1
    question_message_id = await send_next_question(event_type=event_type, question_number=question_number,
                                                   chat_id=callback.message.chat.id, bot=bot)
    await state.update_data(last_question_number=question_number, survey_answers={},
                            message_to_delete=question_message_id, event_type=event_type)


@router.callback_query(StateFilter(SurveyState.survey_started), F.data.startswith('answer_'))
@router.message(StateFilter(SurveyState.survey_started))
async def survey_question_answer_handler(msg: Message | CallbackQuery, state: FSMContext, bot: Bot):
    answer, chat_id = await process_message(message=msg, bot=bot)
    state_data = await state.get_data()
    event_type = state_data.get('event_type')
    if 'message_to_delete' in state_data:
        message_id = state_data.pop('message_to_delete')
        await delete_tg_message(chat_id=chat_id, message_id=message_id, bot=bot)
    current_question_number, survey_answers = state_data.get('last_question_number'), state_data.get('survey_answers')
    if not await validate_answer(chat_id=chat_id, question_number=current_question_number, answer=answer,
                                 state=state, bot=bot, event_type=event_type):
        return None
    survey_answers.update({str(current_question_number): answer})

    if current_question_number != get_survey_question_number(event_type):
        current_question_number += 1
        question_message_id = await send_next_question(event_type=event_type, question_number=current_question_number,
                                                       chat_id=chat_id, bot=bot)
        await state.update_data(last_question_number=current_question_number, survey_answers=survey_answers,
                                message_to_delete=question_message_id)
    else:
        # TODO: add confirmation state, because now, after confirmation send this hanlder still process text and changes last answer
        await state.update_data(survey_answers=survey_answers)
        questions = get_survey_questions(event_type, without_question_data=True)
        message = generate_survey_confirm_text(questions, survey_answers)

        await bot.send_message(chat_id=chat_id, text=message, reply_markup=survey_confirm_menu, parse_mode='Markdown')


@router.callback_query(StateFilter(SurveyState.survey_started), F.data.startswith('surveymenu_confirm'))
async def survey_finish_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    chat_id = callback.message.chat.id
    state_data = await state.get_data()
    user_id, event_type = state_data.get('user_id'), state_data.get('event_type')
    survey_answers = state_data.get('survey_answers')
    questions = get_survey_questions(event_type, without_question_data=True)
    await state.set_state(SurveyState.ready_to_survey)
    await callback.answer()
    await callback.message.delete()
    await bot.send_message(chat_id=chat_id, text=text.survey_finished_message)
    united_answers = unite_questions_and_answers(questions, survey_answers)
    await state.set_state(SurveyState.conception_generating)
    conception = await get_event_conception(event_type, united_answers, int(os.getenv('MAX_RETRIES', 2)))
    await state.set_state(SurveyState.ready_to_survey)
    if not conception:
        return await bot.send_message(chat_id=chat_id, text=text.conception_error, reply_markup=main_menu)

    user_conception_format, full_conception = await format_conception(conception, event_type)
    await save_survey_to_db(user_id, survey_answers, questions, event_type, full_conception)
    await bot.send_message(chat_id=chat_id, text=user_conception_format, parse_mode='Markdown', reply_markup=main_menu)


@router.callback_query(StateFilter(SurveyState.survey_started), F.data.startswith('surveymenu_edit'))
async def survey_edit_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    message_id = callback.message.message_id
    await state.set_state(SurveyState.survey_editing)
    await state.update_data(edited_msg_id=message_id)
    state_data = await state.get_data()
    questions = get_survey_questions(state_data.get('event_type'), without_question_data=True)
    message = 'Выберите какой вопрос вы хотите отредактировать: \n' + '\n'.join(f'{q_number}. {question}'
                                                                                for q_number, question in questions.items())
    await callback.answer()
    await bot.send_message(chat_id=callback.message.chat.id, text=message,
                           reply_markup=generate_survey_edit_menu(questions.keys()).as_markup())


@router.callback_query(StateFilter(SurveyState.survey_editing), F.data.startswith('answeredit_'))
async def edit_button_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    question_number = callback.data.split('_')[-1]
    state_data = await state.get_data()
    event_type = state_data.get('event_type')
    await callback.answer()
    await callback.message.delete()
    question_message_id = await send_next_question(event_type=event_type, question_number=question_number,
                                                   chat_id=callback.message.chat.id, bot=bot)
    await state.update_data(edited_question_number=question_number, message_to_delete=question_message_id)


@router.callback_query(StateFilter(SurveyState.survey_editing))
@router.message(StateFilter(SurveyState.survey_editing))
async def survey_edit_question_answer_handler(msg: Message | CallbackQuery, state: FSMContext, bot: Bot):
    answer, chat_id = await process_message(message=msg, bot=bot)
    state_data = await state.get_data()
    event_type = state_data.get('event_type')
    if 'message_to_delete' in state_data:
        message_id = state_data.pop('message_to_delete')
        await delete_tg_message(chat_id=chat_id, message_id=message_id, bot=bot)
    edit_msg_id = state_data.get('edited_msg_id')
    questions = get_survey_questions(event_type, without_question_data=True)
    edited_question_number, survey_answers = state_data.get('edited_question_number'), state_data.get('survey_answers')
    if not await validate_answer(chat_id=chat_id, question_number=edited_question_number, answer=answer,
                                 state=state, bot=bot, event_type=event_type):
        return None
    survey_answers.update({str(edited_question_number): answer})
    await state.set_state(SurveyState.survey_started)
    await state.update_data(survey_answers=survey_answers)
    message = generate_survey_confirm_text(questions, survey_answers)
    await bot.edit_message_text(chat_id=chat_id, message_id=edit_msg_id, text=message,
                                reply_markup=survey_confirm_menu, parse_mode='Markdown')
