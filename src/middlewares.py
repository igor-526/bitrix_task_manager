from typing import Callable, Dict, Any, Awaitable
from typing import Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from create_bot import bot
import asyncio
from funcs.bitrix_auth import get_user_id_by_tg


class AuthLogsMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        state_data = await data.get("state").get_data()
        if "bitrix_id" not in state_data:
            bitrix_id = await get_user_id_by_tg(event.from_user.id)
            if not bitrix_id:
                await bot.send_message(
                    chat_id=event.from_user.id,
                    text=f"Не удалось найти Вашу учётную запись Bitrix24.\n"
                         f"Для привязки отправьте администратору Bitrix24 "
                         f"следующую информацию:\n\n"
                         f"TELEGRAM_ID: <code>{event.from_user.id}</code>"
                )
                return None
            await data.get("state").update_data(bitrix_id=bitrix_id)
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
