from FSM import TasksFSM

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from create_bitrix import AsyncBitrixClient

from funcs.bitrix_tasks import (f_bitrix_get_created_tasks,
                                f_bitrix_get_my_tasks,
                                f_bitrix_tasks_keep)

from keyboards.task_keyboards import get_tasks_list_keyboard

router = Router(name=__name__)


@router.message(StateFilter(None),
                F.text == "Мои задачи")
async def h_mainmenu_my_tasks(message: types.Message,
                              bitrix: AsyncBitrixClient) -> None:
    tasks = [{"text": f'{task["title"]} ({task["responsible"]["name"]})',
              "id": task["id"]} for task in
             await f_bitrix_get_my_tasks(bitrix)]
    if not tasks:
        await message.answer(text="Вам не поставлена ни одна задача")
        return None
    await message.reply(text="Вот задачи, которые вам поставлены:",
                        reply_markup=get_tasks_list_keyboard(tasks))


@router.message(StateFilter(None),
                F.text == "Поставленные задачи")
async def h_mainmenu_created_tasks(message: types.Message,
                                   bitrix: AsyncBitrixClient) -> None:
    tasks = [{"text": f'{task["title"]} ({task["responsible"]["name"]})',
              "id": task["id"]} for task in
             await f_bitrix_get_created_tasks(bitrix)]
    if not tasks:
        await message.answer(text="Нет задач, которые вы поставили "
                                  "или в которых вы являетесь наблюдателем")
        return None
    await message.reply(text="Вот задачи, которые вы поставили или "
                             "в которых вы являетесь наблюдателем:",
                        reply_markup=get_tasks_list_keyboard(tasks))


@router.message(StateFilter(None))
async def h_mainmenu_add_task(message: types.Message,
                              state: FSMContext) -> None:
    if not message.text:
        await message.reply(text="В ЗАДАЧУ МОЖНО ДОБАВИТЬ ТОЛЬКО ТЕКСТ")
        return None
    await state.set_state(TasksFSM.creating_task)
    await f_bitrix_tasks_keep(message, state)
