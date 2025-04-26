from aiogram.fsm.state import StatesGroup, State


class TasksFSM(StatesGroup):
    creating_task = State()
