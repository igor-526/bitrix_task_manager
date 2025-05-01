import datetime
from typing import Dict, List

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from create_bitrix import AsyncBitrixClient

from funcs.bitrix_users import bitrix_get_users

from keyboards.task_keyboards import creating_task_keyboard, get_task_keyboard


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
    bitrix: AsyncBitrixClient

    def __init__(self, bitrix: AsyncBitrixClient) -> None:
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
        self.bitrix = bitrix

    def init_task_from_sd(self, state_data: dict) -> None:
        full_comment = "\n".join(state_data["comment"])
        self.title = full_comment.replace("\n", " ")[:40]
        self.description = full_comment
        self.created_by = self.bitrix.user_id
        self.responsible_id = self.bitrix.user_id
        self.deadline = datetime.datetime.now() + datetime.timedelta(days=1)

    async def init_task_from_id(self, task_id: int) \
            -> Dict[str: bool, str: str | None]:
        task = await self.bitrix.get(endpoint='tasks.task.list',
                                     filter_params={'ID': task_id})
        task = task["result"]["tasks"]
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
            self.bitrix,
            [self.created_by, self.responsible_id,
             *self.accomplices, *self.auditors])

    async def add_task(self) -> Dict[str: bool, str: str | None]:
        task = await self.bitrix.post('tasks.task.add', {
            'TITLE': self.title,
            'DESCRIPTION': self.description,
            "PRIORITY": 1,
            'CREATED_BY': self.created_by,
            'RESPONSIBLE_ID': self.responsible_id,
            'ACCOMPLICES': [],
            'AUDITORS': [],
            'DEADLINE': self.deadline
        })
        self.id = task["result"]["task"].get('id')
        await self.update_all_users_info()
        return {
            "status": True,
            "error": None
        }

    async def generate_task_message(self) \
            -> Dict[str: str, str: None]:
        msg_text = ""
        msg_text += f'<b>Наименование</b>: {self.title}\n'
        msg_text += f'<b>Описание</b>: {self.description}\n'
        return {
            "text": msg_text,
            "reply_markup": get_task_keyboard(self, self.bitrix.user_id)
        }

    async def update(self) -> Dict[str: str, str | None]:
        fields = dict()
        if self.created_by:
            fields["CREATED_BY"] = self.created_by
        if self.responsible_id:
            fields["RESPONSIBLE_ID"] = self.responsible_id
        if self.accomplices:
            fields["ACCOMPLICES"] = self.accomplices
        if self.auditors:
            fields["AUDITORS"] = self.auditors
        if self.deadline:
            fields["DEADLINE"] = self.deadline
        if self.priority:
            fields["PRIORITY"] = self.priority
        if self.title:
            fields["TITLE"] = self.title
        if self.description:
            fields["DESCRIPTION"] = self.description
        try:
            await self.bitrix.post('tasks.task.update',
                                   fields=fields,
                                   taskId=self.id)
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


async def f_bitrix_get_created_tasks(bitrix: AsyncBitrixClient) \
        -> List[Dict[str: str, str: List]]:
    tasks_created = await bitrix.get('tasks.task.list',
                                     select_params=["ID", "TITLE",
                                                    "RESPONSIBLE_ID"],
                                     filter_params={
                                         "CREATED_BY": bitrix.user_id
                                     })
    tasks_auditor = await bitrix.get('tasks.task.list',
                                     select_params=["ID", "TITLE",
                                                    "RESPONSIBLE_ID"],
                                     filter_params={"AUDITOR": bitrix.user_id})
    return [*tasks_created['result']['tasks'],
            *tasks_auditor['result']['tasks']]


async def f_bitrix_get_my_tasks(bitrix: AsyncBitrixClient) \
        -> List[Dict[str: str, str: List]]:
    select_params = ["ID", "TITLE", "DEADLINE", "RESPONSIBLE_ID"]
    filter_params = {"RESPONSIBLE_ID": bitrix.user_id}
    tasks = await bitrix.get(endpoint='tasks.task.list',
                             select_params=select_params,
                             filter_params=filter_params)
    return tasks['result']['tasks']
