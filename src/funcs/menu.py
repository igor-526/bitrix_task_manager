from aiogram.fsm.context import FSMContext

from create_bot import bot

from keyboards.menu_keyboards import menu_keyboard


async def f_send_menu(tg_id: int, state: FSMContext) -> None:
    state_data = await state.get_data()
    bitrix_id = state_data.get('bitrix_id')
    await state.clear()
    await bot.send_message(chat_id=tg_id,
                           text="Выберите действие или начните вводить задачу",
                           reply_markup=menu_keyboard)
    if bitrix_id:
        await state.update_data(bitrix_id=bitrix_id)
