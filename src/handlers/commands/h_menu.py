from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from FSM import TasksFSM
from funcs.bitrix_tasks import (f_bitrix_tasks_keep,
                                f_bitrix_get_created_tasks,
                                f_bitrix_get_my_tasks)
from keyboards.task_keyboards import get_tasks_list_keyboard

router = Router(name=__name__)


@router.message(StateFilter(None),
                F.text == "Мои задачи")
async def h_mainmenu_my_tasks(message: types.Message,
                              state: FSMContext) -> None:
    state_data = await state.get_data()
    tasks = [{"text": f'{task["title"]} ({task["responsible"]["name"]})',
              "id": task["id"]} for task in
             await f_bitrix_get_my_tasks(state_data.get("bitrix_id"))]
    if not tasks:
        await message.answer(text="Вам не поставлена ни одна задача")
        return None
    await message.reply(text="Вот задачи, которые вам поставлены:",
                        reply_markup=get_tasks_list_keyboard(tasks))


@router.message(StateFilter(None),
                F.text == "Поставленные задачи")
async def h_mainmenu_created_tasks(message: types.Message,
                                   state: FSMContext) -> None:
    state_data = await state.get_data()
    tasks = [{"text": f'{task["title"]} ({task["responsible"]["name"]})',
              "id": task["id"]} for task in
             await f_bitrix_get_created_tasks(state_data.get("bitrix_id"))]
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
