from aiogram.fsm.state import StatesGroup, State


class AdvertisingStates(StatesGroup):
    advertising_survey_started = State()


class SurveyState(StatesGroup):
    chat_started = State()
    choosing_event_type_for_order = State()
    deciding_whether_to_generate_conception = State()
    ready_to_survey = State()
    survey_started = State()
    survey_editing = State()
    conception_generating = State()
