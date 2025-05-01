from aiogram import F, Router
from aiogram.types import CallbackQuery

from create_bitrix import AsyncBitrixClient

from create_bot import bot

from funcs.bitrix_tasks import BitrixTask

from keyboards.task_keyboards import (TaskChangeParticipantsCallback,
                                      TaskMainCallback)
from keyboards.users_keyboard import get_all_users_keyboard

router = Router(name=__name__)


@router.callback_query(TaskMainCallback.filter(
    F.action == "change_created_by"))
async def h_tasks_change_created_by(callback: CallbackQuery,
                                    callback_data: TaskMainCallback,
                                    bitrix: AsyncBitrixClient) -> None:
    task = BitrixTask(bitrix)
    result = await task.init_task_from_id(callback_data.task_id)
    if result.get("status") is False:
        await callback.answer("Ошибка! Задача не найдена")
        await callback.message.delete()
        return None
    await callback.message.edit_text(
        text="Выберите нового постановщика:",
        reply_markup=await get_all_users_keyboard(
            bitrix=bitrix,
            callback_data=TaskChangeParticipantsCallback(
                task_id=callback_data.task_id,
                action="created_by",
                user_id=0
            ),
            accept_symbol=[task.created_by],
            cross_symbol=[]
        ))


@router.callback_query(TaskChangeParticipantsCallback.filter(
    F.action == "created_by"))
async def h_tasks_change_created_by_apply(callback: CallbackQuery,
                                          callback_data:
                                          TaskChangeParticipantsCallback,
                                          bitrix: AsyncBitrixClient) -> None:
    task = BitrixTask(bitrix)
    task.id = callback_data.task_id
    task.created_by = callback_data.user_id
    result = await task.update()
    if result.get("status"):
        await task.init_task_from_id(callback_data.task_id)
        await task.update_all_users_info()
        await callback.message.edit_text(**await task.generate_task_message())
    if result.get("status") is False:
        await bot.send_message(chat_id=callback.from_user.id,
                               text=f'Произошла ошибка\n'
                                    f'{result.get("error")}')
        await callback.message.delete()
        return None
