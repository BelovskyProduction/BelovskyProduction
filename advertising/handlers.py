from aiogram import Bot
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from magic_filter import F

from user_states import SurveyState

advertising_router = Router(name='advertising_router')


@advertising_router.message(F.text == f'{chr(0x1F4E2)} Реклама')
async def start_advertising_survey_handler(msg: Message, state: FSMContext, bot: Bot):
    print(1)
    await msg.delete()
    current_state = await state.get_state()

    if current_state in [SurveyState.ready_to_survey.state]:
        data = await state.get_data()
        print('here')
        # if not await check_if_user_can_start_survey(data.get('user_id')):
        #     return await msg.answer(text=text.surveys_limit_reached)
        #
        # await state.set_state(SurveyState.survey_started)
        # events = [event for event in event_types if event != 'Другое']
        # menu = generate_event_type_menu(events)
        # await msg.answer(text=text.event_choose_message, reply_markup=menu.as_markup(), parse_mode='Markdown')
