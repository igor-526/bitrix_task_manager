from aiogram.fsm.state import State, StatesGroup


class TasksFSM(StatesGroup):
    creating_task = State()
