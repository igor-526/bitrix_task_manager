from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

created_tasks = KeyboardButton(text="Поставленные задачи")
my_tasks = KeyboardButton(text="Мои задачи")

menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                    keyboard=[[created_tasks], [my_tasks]])
