from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_menu_buttons = [[KeyboardButton(text=f'{chr(0x1F4CB)} Опрос')]]

main_menu = ReplyKeyboardMarkup(keyboard=main_menu_buttons, resize_keyboard=True, one_time_keyboard=False, row_width=2)

survey_confirm_menu_buttons = [[InlineKeyboardButton(text=f'{chr(0x2705)} Закончить опрос',
                                                     callback_data='surveymenu_confirm')],
                               [InlineKeyboardButton(text=f'{chr(0x270F)} Редактировать',
                                                     callback_data='surveymenu_edit')]]
survey_confirm_menu = InlineKeyboardMarkup(inline_keyboard=survey_confirm_menu_buttons)


def generate_survey_edit_menu(question_numbers):
    builder = InlineKeyboardBuilder()

    for q_number in question_numbers:
        builder.button(text=str(q_number), callback_data=f'answeredit_{q_number}')
    builder.adjust(5)
    return builder
