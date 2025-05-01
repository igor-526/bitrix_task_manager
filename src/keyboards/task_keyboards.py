import datetime
from typing import Dict, List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import (InlineKeyboardMarkup,
                           KeyboardButton,
                           ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder

add_task_button = KeyboardButton(text="Добавить задачу")
cancel_button = KeyboardButton(text="Отмена")

creating_task_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                             keyboard=[
                                                 [add_task_button],
                                                 [cancel_button]
                                             ])


class TaskMainCallback(CallbackData, prefix="task"):
    task_id: int
    action: str


class TaskChangeParticipantsCallback(CallbackData, prefix="task_change"):
    task_id: int
    action: str
    user_id: int


class TaskChangeDeadlineCallback(CallbackData, prefix="task_change_deadline"):
    task_id: int
    year: int
    month: int
    day: int
    hour: int


def get_tasks_list_keyboard(tasks: List[Dict[str: str, str: str]]) \
        -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for task in tasks:
        builder.button(
            text=task["text"],
            callback_data=TaskMainCallback(
                task_id=task["id"],
                action="show"
            )
        )
    builder.adjust(1)
    return builder.as_markup()


def get_task_keyboard(task, user_id: int) -> InlineKeyboardMarkup:
    def add_created_by_button():
        created_by_user_text = list(filter(
            lambda user: user.get("id") == str(task.created_by),
            task.all_users_info
        ))
        created_by_user_text = (
            f'{created_by_user_text[0].get("first_name")} '
            f'{created_by_user_text[0].get("last_name")}'
        ) \
            if created_by_user_text else "Отсутствует"
        builder.button(
            text=f"Постановщик: {created_by_user_text}",
            callback_data=TaskMainCallback(task_id=task.id,
                                           action="change_created_by")
        )

    def add_responsible_button():
        responsible_user_text = list(filter(
            lambda user: user.get("id") == str(task.responsible_id),
            task.all_users_info
        ))
        responsible_user_text = (
            f'{responsible_user_text[0].get("first_name")} '
            f'{responsible_user_text[0].get("last_name")}'
        ) \
            if responsible_user_text else "Отсутствует"
        builder.button(
            text=f"Исполнитель: {responsible_user_text}",
            callback_data=TaskMainCallback(task_id=task.id,
                                           action="change_responsible")
        )

    def add_deadline_button():
        text = task.deadline.strftime('%d.%m.%Y %H:%M') if (
            task.deadline) else 'Не установлен'
        builder.button(
            text=f"Срок: {text}",
            callback_data=TaskMainCallback(task_id=task.id,
                                           action="change_deadline")
        )

    print(task.all_users_info)
    builder = InlineKeyboardBuilder()
    add_created_by_button()
    add_responsible_button()
    add_deadline_button()
    builder.button(text="Открыть",
                   url=f"https://cp.znanied.ru/company/personal/user/"
                       f"{user_id}/tasks/task/view/{task.id}/")
    builder.adjust(1)
    return builder.as_markup()


def get_deadline_buttons(task_id: int) -> InlineKeyboardMarkup:
    def get_datetime_dict(timedelta_days: int, timemode: int = 1) -> dict:
        date = (datetime.datetime.now() +
                datetime.timedelta(days=timedelta_days)) if (
            timedelta_days) else datetime.datetime.now()
        if timemode == 1:
            date = date.replace(hour=12)
        elif timemode == 2:
            date = date.replace(hour=20)
        return {
            "year": date.year,
            "month": date.month,
            "day": date.day,
            "hour": date.hour,
        }

    builder = InlineKeyboardBuilder()

    builder.button(text="Сегодня 12:00",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(0, 1)
                   ))
    builder.button(text="Сегодня 20:00",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(0, 2)
                   ))
    builder.button(text="Завтра 12:00",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(1, 1)
                   ))
    builder.button(text="Завтра 20ч",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(1, 2)
                   ))
    builder.button(text="Послезавтра 12ч",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(2, 1)
                   ))
    builder.button(text="Послезавтра 20ч",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(2, 2)
                   ))
    builder.button(text="Через 3 дня 12ч",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(3, 1)
                   ))
    builder.button(text="Через 3 дня 20ч",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(3, 2)
                   ))
    builder.button(text="Через неделю",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(7, 1)
                   ))
    builder.button(text="Через 2 недели",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(14, 1)
                   ))
    builder.button(text="Через 3 недели",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(21, 1)
                   ))
    builder.button(text="Через месяц",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(30, 1)
                   ))
    builder.button(text="Через 2 месяца",
                   callback_data=TaskChangeDeadlineCallback(
                       task_id=task_id,
                       **get_datetime_dict(31, 1)
                   ))
    builder.button(text="Вернуться",
                   callback_data=TaskMainCallback(
                       task_id=task_id,
                       action="show"
                   ))

    builder.adjust(2)
    return builder.as_markup()
