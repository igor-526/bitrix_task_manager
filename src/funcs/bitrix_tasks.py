import datetime
from typing import List, Dict
from aiogram.fsm.context import FSMContext
from create_bitrix import bitrix
from funcs.bitrix_users import bitrix_get_users
from keyboards.task_keyboards import get_task_keyboard, creating_task_keyboard
from aiogram.types import Message


class BitrixTask:
    id: int | None
    title: str | None
    description: str | None
    priority: int | None
    created_by: int | None
    responsible_id: int | None
    deadline: datetime.datetime | None
    accomplices: List[int]
    auditors: List[int]
    all_users_info: List[Dict]

    def __init__(self) -> None:
        self.accomplices = []
        self.auditors = []
        self.all_users_info = []
        self.priority = None
        self.id = None
        self.title = None
        self.description = None
        self.created_by = None
        self.responsible_id = None
        self.deadline = None

    def init_task_from_sd(self, state_data: dict) -> None:
        full_comment = "\n".join(state_data["comment"])
        self.title = full_comment.replace("\n", " ")[:40]
        self.description = full_comment
        self.created_by = state_data.get("bitrix_id")
        self.responsible_id = state_data.get("bitrix_id")
        self.deadline = datetime.datetime.now() + datetime.timedelta(days=1)

    async def init_task_from_id(self, task_id: int) \
            -> Dict[str: bool, str: str | None]:
        task = await bitrix.get_all('tasks.task.list', params={
            'filter': {'ID': task_id},
        })
        if task:
            self.id = int(task[0].get("id"))
            self.title = task[0].get("title")
            self.description = task[0].get("description")
            self.priority = task[0].get("priority")
            self.created_by = int(task[0].get("createdBy"))
            self.responsible_id = int(task[0].get("responsibleId"))
            self.deadline = datetime.datetime.strptime(task[0].get("deadline"),
                                                       "%Y-%m-%dT%H:%M:%S%z") \
                if task[0].get("deadline") else None
            self.accomplices = task[0].get("accomplices")
            self.auditors = task[0].get("auditors")
            return {"status": True,
                    "error": None}
        else:
            return {"status": False,
                    "error": "Задача не найдена"}

    async def update_all_users_info(self) -> None:
        self.all_users_info = await bitrix_get_users(
            [self.created_by, self.responsible_id,
             *self.accomplices, *self.auditors])

    async def add_task(self) -> Dict[str: bool, str: str | None]:
        try:
            task = await bitrix.call('tasks.task.add', {
                'fields': {
                    'TITLE': self.title,
                    'DESCRIPTION': self.description,
                    "PRIORITY": 1,
                    'CREATED_BY': self.created_by,
                    'RESPONSIBLE_ID': self.responsible_id,
                    'ACCOMPLICES': [],
                    'AUDITORS': [],
                    'DEADLINE': self.deadline
                }})
            self.id = task.get('id')
            await self.update_all_users_info()
            return {
                "status": True,
                "error": None
            }
        except Exception as e:
            return {
                "status": False,
                "error": str(e)
            }

    async def generate_task_message(self, user_id: int) \
            -> Dict[str: str, str: None]:
        msg_text = ""
        msg_text += f'<b>Наименование</b>: {self.title}\n'
        msg_text += f'<b>Описание</b>: {self.description}\n'
        return {
            "text": msg_text,
            "reply_markup": get_task_keyboard(self, user_id)
        }

    async def update(self) -> Dict[str: str, str | None]:
        params = {
            "taskId": self.id,
            "fields": {}
        }
        if self.created_by:
            params["fields"]["CREATED_BY"] = self.created_by
        if self.responsible_id:
            params["fields"]["RESPONSIBLE_ID"] = self.responsible_id
        if self.accomplices:
            params["fields"]["ACCOMPLICES"] = self.accomplices
        if self.auditors:
            params["fields"]["AUDITORS"] = self.auditors
        if self.deadline:
            params["fields"]["DEADLINE"] = self.deadline
        if self.priority:
            params["fields"]["PRIORITY"] = self.priority
        if self.title:
            params["fields"]["TITLE"] = self.title
        if self.description:
            params["fields"]["DESCRIPTION"] = self.description
        try:
            await bitrix.call('tasks.task.update', params)
            return {"status": True,
                    "error": None}
        except Exception as e:
            return {"status": False,
                    "error": str(e)}


async def f_bitrix_tasks_keep(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("В ЗАДАЧУ МОЖНО ДОБАВИТЬ ТОЛЬКО ТЕКСТ")
        return None
    state_data = await state.get_data()
    if not state_data.get("files") and not state_data.get("comment"):
        await state.set_data({'files': [],
                              'comment': []})
    state_data = await state.get_data()
    state_data["comment"].append(message.text)
    await state.set_data(state_data)
    await message.reply(text="Принято\n"
                             "Пришлите ещё сообщения или выберите действие",
                        reply_markup=creating_task_keyboard)


async def f_bitrix_get_created_tasks(bitrix_id: int) \
        -> List[Dict[str: str, str: List]]:
    tasks_created = await bitrix.get_all('tasks.task.list', params={
        'filter': {"CREATED_BY": bitrix_id},
        'select': ["ID", "TITLE", "RESPONSIBLE_ID"]
    })
    tasks_auditor = await bitrix.get_all('tasks.task.list', params={
        'filter': {"AUDITOR": bitrix_id},
        'select': ["ID", "TITLE", "RESPONSIBLE_ID"]
    })
    return [*tasks_created, *tasks_auditor]


async def f_bitrix_get_my_tasks(bitrix_id: int) \
        -> List[Dict[str: str, str: List]]:
    tasks = await bitrix.get_all('tasks.task.list', params={
        'filter': {"RESPONSIBLE_ID": bitrix_id},
        'select': ["ID", "TITLE", "DEADLINE", "RESPONSIBLE_ID"]
    })
    return tasks
