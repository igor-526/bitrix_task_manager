from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from FSM import TasksFSM
from create_bot import bot
from funcs.bitrix_tasks import BitrixTask, f_bitrix_tasks_keep
from funcs.menu import f_send_menu
from keyboards.task_keyboards import TaskMainCallback

router = Router(name=__name__)


@router.callback_query(TaskMainCallback.filter(F.action == "show"))
async def h_tasks_show(callback: CallbackQuery,
                       callback_data: TaskMainCallback,
                       state: FSMContext) -> None:
    await callback.message.delete()
    task = BitrixTask()
    task_result = await task.init_task_from_id(callback_data.task_id)
    if task_result.get("status"):
        await task.update_all_users_info()
        state_data = await state.get_data()
        task_message = await task.generate_task_message(
            int(state_data.get("bitrix_id")))
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
                           state: FSMContext) -> None:
    task = BitrixTask()
    task.init_task_from_sd(await state.get_data())
    task_result = await task.add_task()
    if task_result.get("status"):
        state_data = await state.get_data()
        task_message = await task.generate_task_message(
            int(state_data.get("bitrix_id")))
        await message.answer(**task_message)
    else:
        await message.answer(text=f'Не удалось добавить задачу\n'
                                  f'Ошибка: {task_result.get("error")}')
    await f_send_menu(message.from_user.id, state)


@router.message(StateFilter(TasksFSM.creating_task))
async def h_tasks_keep(message: Message, state: FSMContext) -> None:
    await f_bitrix_tasks_keep(message, state)
