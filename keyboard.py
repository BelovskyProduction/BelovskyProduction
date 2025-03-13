from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_menu_buttons = [[KeyboardButton(text=f'{chr(0x1F4CB)} Опрос')]]

main_menu = ReplyKeyboardMarkup(keyboard=main_menu_buttons, resize_keyboard=True, one_time_keyboard=False, row_width=2)

survey_request_menu_buttons = [[InlineKeyboardButton(text=f'Да',
                                                     callback_data='surveyrequest_yes')],
                               [InlineKeyboardButton(text=f'Нет',
                                                     callback_data='surveyrequest_no')]]
survey_confirm_menu_buttons = [[InlineKeyboardButton(text=f'{chr(0x2705)} Закончить опрос',
                                                     callback_data='surveymenu_confirm'),
                                InlineKeyboardButton(text=f'{chr(0x270F)} Редактировать',
                                                     callback_data='surveymenu_edit')
                                ]]
survey_confirm_menu = InlineKeyboardMarkup(inline_keyboard=survey_confirm_menu_buttons)
survey_request_menu = InlineKeyboardMarkup(inline_keyboard=survey_request_menu_buttons)


def generate_event_type_menu(event_types):
    builder = InlineKeyboardBuilder()

    for event in event_types:
        builder.button(text=str(event), callback_data=f'event_{event}')
    builder.adjust(2)
    return builder


def generate_survey_edit_menu(question_numbers):
    builder = InlineKeyboardBuilder()

    for q_number in question_numbers:
        builder.button(text=str(q_number), callback_data=f'answeredit_{q_number}')
    builder.adjust(5)
    return builder


def generate_question_answer_menu(answers: list):
    builder = InlineKeyboardBuilder()

    for answer in answers:
        builder.button(text=str(answer), callback_data=f'answer_{answer}')
    builder.adjust(3)
    return builder.as_markup()
