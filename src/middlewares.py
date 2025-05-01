import asyncio
from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from create_bitrix import AsyncBitrixClient, BitrixException

from create_bot import bot

from database.engine import async_session_maker
from database.models import User

from keyboards.menu_keyboards import get_authorize_button

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker


class ExceptionLoggingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Union[Message, CallbackQuery],
                               Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except BitrixException as ex:
            error = ex.message
            if error == "NO_AUTH_FOUND":
                error = "Нет данных для авторизации"
            elif error == "invalid_token":
                async with async_session_maker() as session:
                    query = delete(User).where(
                        User.tg_id == event.from_user.id
                    )
                    await session.execute(query)
                    await session.commit()
                await bot.send_message(
                    chat_id=event.from_user.id,
                    text='Произошла ошибка в авторизации:\n'
                         'Пожалуйста, войдите снова',
                    reply_markup=get_authorize_button(event.from_user.id)
                )
                return None
            await bot.send_message(chat_id=event.from_user.id,
                                   text=f'Произошла ошибка в работе бота:\n'
                                        f'{error}')


class SetAccessTokenMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[Union[Message, CallbackQuery],
                               Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        async with self.session_pool() as session:
            query = select(User).where(User.tg_id == event.from_user.id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            if not user:
                await bot.send_message(
                    chat_id=event.from_user.id,
                    text="Нажмите на кнопку для авторизации на портале",
                    reply_markup=get_authorize_button(event.from_user.id)
                )
                return None
            data['bitrix'] = AsyncBitrixClient(
                access_token=user.access_token,
                refresh_token=user.refresh_token,
                user_id=user.bx_id
            )
        return await handler(event, data)


class MediaMiddleware(BaseMiddleware):
    def __init__(self, latency: Union[int, float] = 0.05):
        self.medias = {}
        self.latency = latency
        super(MediaMiddleware, self).__init__()

    async def __call__(
            self,
            handler: Callable[[Union[Message, CallbackQuery],
                               Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:

        if isinstance(event, Message) and event.media_group_id:
            try:
                self.medias[event.media_group_id].append(event)
                return
            except KeyError:
                self.medias[event.media_group_id] = [event]
                await asyncio.sleep(self.latency)
                data["media_events"] = self.medias.pop(event.media_group_id)
        return await handler(event, data)
