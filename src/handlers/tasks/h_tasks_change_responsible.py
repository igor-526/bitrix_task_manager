from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from create_bot import bot
from funcs.bitrix_tasks import BitrixTask
from keyboards.task_keyboards import (TaskMainCallback,
                                      TaskChangeParticipantsCallback)
from keyboards.users_keyboard import get_all_users_keyboard

router = Router(name=__name__)


@router.callback_query(TaskMainCallback.filter(
    F.action == "change_responsible")
)
async def h_tasks_change_responsible(callback: CallbackQuery,
                                     callback_data: TaskMainCallback) \
        -> None:
    task = BitrixTask()
    result = await task.init_task_from_id(callback_data.task_id)
    if result.get("status") is False:
        await callback.answer("Ошибка! Задача не найдена")
        await callback.message.delete()
        return None
    await callback.message.edit_text(
        text="Выберите нового исполнителя:",
        reply_markup=await get_all_users_keyboard(
            callback_data=TaskChangeParticipantsCallback(
                task_id=callback_data.task_id,
                action="responsible",
                user_id=0
            ),
            accept_symbol=[task.responsible_id],
            cross_symbol=[]
        ))


@router.callback_query(TaskChangeParticipantsCallback.filter(
    F.action == "responsible")
)
async def h_tasks_change_responsible_apply(callback: CallbackQuery,
                                           callback_data:
                                           TaskChangeParticipantsCallback,
                                           state: FSMContext) -> None:
    task = BitrixTask()
    task.id = callback_data.task_id
    task.responsible_id = callback_data.user_id
    result = await task.update()
    if result.get("status"):
        await task.init_task_from_id(callback_data.task_id)
        await task.update_all_users_info()
        state_data = await state.get_data()
        await callback.message.edit_text(
            **await task.generate_task_message(
                int(state_data.get("bitrix_id"))
            )
        )
    if result.get("status") is False:
        await bot.send_message(chat_id=callback.from_user.id,
                               text=f'Произошла ошибка\n'
                                    f'{result.get("error")}')
        await callback.message.delete()
        return None
