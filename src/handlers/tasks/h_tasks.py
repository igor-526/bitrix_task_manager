from FSM import TasksFSM

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from create_bitrix import AsyncBitrixClient

from create_bot import bot

from funcs.bitrix_tasks import BitrixTask, f_bitrix_tasks_keep
from funcs.menu import f_send_menu

from keyboards.task_keyboards import TaskMainCallback

router = Router(name=__name__)


@router.callback_query(TaskMainCallback.filter(F.action == "show"))
async def h_tasks_show(callback: CallbackQuery,
                       callback_data: TaskMainCallback,
                       bitrix: AsyncBitrixClient) -> None:
    await callback.message.delete()
    task = BitrixTask(bitrix)
    task_result = await task.init_task_from_id(callback_data.task_id)
    if task_result.get("status"):
        await task.update_all_users_info()
        task_message = await task.generate_task_message()
        await bot.send_message(chat_id=callback.from_user.id,
                               **task_message)
    else:
        await bot.send_message(chat_id=callback.from_user.id,
                               text=f'Не удалось добавить задачу\n'
                                    f'Ошибка: {task_result.get("error")}')


@router.message(StateFilter(TasksFSM.creating_task),
                F.text == "Отмена")
async def h_tasks_cancel(message: Message,
                         state: FSMContext) -> None:
    await f_send_menu(message.from_user.id, state)


@router.message(StateFilter(TasksFSM.creating_task),
                F.text == "Добавить задачу")
async def h_tasks_add_task(message: Message,
                           state: FSMContext,
                           bitrix: AsyncBitrixClient) -> None:
    task = BitrixTask(bitrix)
    task.init_task_from_sd(await state.get_data())
    task_result = await task.add_task()
    if task_result.get("status"):
        task_message = await task.generate_task_message()
        await message.answer(**task_message)
    else:
        await message.answer(text=f'Не удалось добавить задачу\n'
                                  f'Ошибка: {task_result.get("error")}')
    await f_send_menu(message.from_user.id, state)


@router.message(StateFilter(TasksFSM.creating_task))
async def h_tasks_keep(message: Message, state: FSMContext) -> None:
    await f_bitrix_tasks_keep(message, state)
