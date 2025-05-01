from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

from settings import BITRIX_BASE_URL, BITRIX_CLIENT_ID


created_tasks = KeyboardButton(text="Поставленные задачи")
my_tasks = KeyboardButton(text="Мои задачи")

menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                    keyboard=[[created_tasks], [my_tasks]])


def get_authorize_button(tg_id: int) -> InlineKeyboardMarkup:
    authorize_button = InlineKeyboardButton(
        text="Авторизация",
        url=f"{BITRIX_BASE_URL}oauth/authorize/?"
            f"client_id={BITRIX_CLIENT_ID}&"
            f"state={str(tg_id)}"
    )
    return InlineKeyboardMarkup(inline_keyboard=[[authorize_button]])
