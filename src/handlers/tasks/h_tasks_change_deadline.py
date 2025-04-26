import datetime
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from create_bot import bot
from funcs.bitrix_tasks import BitrixTask
from keyboards.task_keyboards import (TaskMainCallback,
                                      get_deadline_buttons,
                                      TaskChangeDeadlineCallback)

router = Router(name=__name__)


@router.callback_query(TaskMainCallback.filter(F.action == "change_deadline"))
async def h_tasks_change_deadline(callback: CallbackQuery,
                                  callback_data: TaskMainCallback) -> None:
    await callback.message.edit_text(text="Выберите срок выполнения задачи:",
                                     reply_markup=get_deadline_buttons(
                                         callback_data.task_id))


@router.callback_query(TaskChangeDeadlineCallback.filter())
async def h_tasks_change_deadline_apply(callback: CallbackQuery,
                                        callback_data:
                                        TaskChangeDeadlineCallback,
                                        state: FSMContext) -> None:
    task = BitrixTask()
    task.id = callback_data.task_id
    task.deadline = datetime.datetime(
        year=callback_data.year,
        month=callback_data.month,
        day=callback_data.day,
        hour=callback_data.hour,
        minute=0,
        second=0,
    )
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
