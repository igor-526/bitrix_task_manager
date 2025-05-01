from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from create_bitrix import AsyncBitrixClient

from funcs.bitrix_users import bitrix_get_users


async def get_all_users_keyboard(bitrix: AsyncBitrixClient,
                                 callback_data: CallbackData,
                                 accept_symbol: list = None,
                                 cross_symbol: list = None) \
        -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if accept_symbol is None:
        accept_symbol = []
    if cross_symbol is None:
        cross_symbol = []
    all_users = await bitrix_get_users(bitrix)
    for user in all_users:
        text = ""
        if int(user.get("id")) in accept_symbol:
            text += "\u2705 "
        if int(user.get("id")) in cross_symbol:
            text += "\u274C "
        text += f'{user.get("first_name")} {user.get("last_name")}'
        callback_data.user_id = int(user.get("id"))
        builder.button(
            text=text,
            callback_data=callback_data
        )
    builder.adjust(1)
    return builder.as_markup()
