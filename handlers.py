from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram import F

import text
from keyboard import main_menu, survey_confirm_menu, generate_survey_edit_menu
from service import save_survey_to_db, generate_survey_confirm_text, check_if_user_can_start_survey
from utils import format_message

router = Router()

questions = {1: 'Ваш номер?', 2: 'Ваша почта?', 3: 'Как зовут молодоженов?', 4: 'Сколько лет?', 5: 'Как познакомились?',
             6: 'Какие увлечения/хобби?', 7: 'Любимый цвет', 8: 'Любимые исполнители?',
             9: 'Предпочтительный стиль проведения мероприятия?', 10: 'Любимое время года?', 11: 'Любимая марка авто?'}


class SurveyState(StatesGroup):
    started = State()
    editing = State()


@router.message(Command('start'))
async def start_handler(msg: Message):
    message = format_message(text.welcome_message, username=msg.from_user.username)
    await msg.answer(text=message, reply_markup=main_menu)


@router.message(F.text == f'{chr(0x1F4CB)} Опрос')
async def start_survey_handler(msg: Message, state: FSMContext):
    await msg.delete()
    if not await check_if_user_can_start_survey(msg.from_user.id):
        return await msg.answer(text=text.surveys_limit_reached)

    current_state = await state.get_state()

    if current_state not in [SurveyState.started.state, SurveyState.editing.state]:
        question_number = 1
        await state.set_state(SurveyState.started)
        question = questions.get(question_number)
        send_question = await msg.answer(text=question)
        await state.update_data(last_question_number=question_number, survey_answers={}, message_to_delete=send_question.message_id)


@router.message(StateFilter(SurveyState.started))
async def question_answer_handler(msg: Message, state: FSMContext, bot: Bot):
    answer = msg.text
    state_data = await state.get_data()
    await msg.delete()
    if 'message_to_delete' in state_data:
        message_id = state_data.pop('message_to_delete')
        await bot.delete_message(chat_id=msg.chat.id, message_id=message_id)
    current_question_number, survey_answers = state_data.get('last_question_number'), state_data.get('survey_answers')
    survey_answers.update({current_question_number: answer})

    if current_question_number != len(questions):
        current_question_number += 1
        question = questions.get(current_question_number)
        send_question = await msg.answer(text=question)
        await state.update_data(last_question_number=current_question_number, survey_answers=survey_answers,
                                message_to_delete=send_question.message_id)
    else:
        message = generate_survey_confirm_text(questions, survey_answers)

        await msg.answer(message, reply_markup=survey_confirm_menu, parse_mode='Markdown')


@router.callback_query(StateFilter(SurveyState.started), F.data.startswith('surveymenu_confirm'))
async def survey_finish_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback.from_user.id
    state_data = await state.get_data()
    await save_survey_to_db(user_id, state_data.get('survey_answers'), questions)
    await state.clear()
    await callback.answer()
    await callback.message.delete()
    await bot.send_message(chat_id=callback.message.chat.id, text=text.survey_finished_message)


@router.callback_query(StateFilter(SurveyState.started), F.data.startswith('surveymenu_edit'))
async def survey_edit_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    message_id = callback.message.message_id
    await state.set_state(SurveyState.editing)
    await state.update_data(edited_msg_id=message_id)
    message = 'Выберите какой вопрос вы хотите отредактировать: \n' + '\n'.join(f'{q_number}. {question}'
                                                                                for q_number, question in questions.items())
    await callback.answer()
    await bot.send_message(chat_id=callback.message.chat.id, text=message,
                           reply_markup=generate_survey_edit_menu(questions.keys()).as_markup())


@router.callback_query(StateFilter(SurveyState.editing), F.data.startswith('answeredit_'))
async def edit_button_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    question_number = callback.data.split('_')[-1]
    question = questions.get(int(question_number))
    await callback.answer()
    await callback.message.delete()
    send_question = await bot.send_message(chat_id=callback.message.chat.id, text=question)
    await state.update_data(edited_question_number=question_number, message_to_delete=send_question.message_id)


@router.message(StateFilter(SurveyState.editing))
async def question_answer_handler(msg: Message, state: FSMContext, bot: Bot):
    answer = msg.text
    await msg.delete()
    state_data = await state.get_data()
    if 'message_to_delete' in state_data:
        message_id = state_data.pop('message_to_delete')
        await bot.delete_message(chat_id=msg.chat.id, message_id=message_id)
    edit_msg_id = state_data.get('edited_msg_id')
    edited_question_number, survey_answers = state_data.get('edited_question_number'), state_data.get('survey_answers')
    survey_answers.update({int(edited_question_number): answer})
    await state.set_state(SurveyState.started)
    await state.update_data(survey_answers=survey_answers)
    message = generate_survey_confirm_text(questions, survey_answers)
    await bot.edit_message_text(chat_id=msg.chat.id, message_id=edit_msg_id, text=message,
                                reply_markup=survey_confirm_menu, parse_mode='Markdown')
