from aiogram.fsm.state import StatesGroup, State


class AdvertisingStates(StatesGroup):
    pass


class SurveyState(StatesGroup):
    chat_started = State()
    choosing_event_type_for_order = State()
    deciding_whether_to_generate_conception = State()
    ready_to_survey = State()
    survey_started = State()
    survey_editing = State()
    conception_generating = State()
