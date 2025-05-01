import asyncio
import logging

from create_bot import bot, dp

from database.engine import async_session_maker, create_db

from handlers import router as main_router

from middlewares import MediaMiddleware, SetAccessTokenMiddleware


async def bot_start_polling() -> None:
    await create_db()
    dp.include_routers(main_router)
    dp.message.middleware.register(
        SetAccessTokenMiddleware(async_session_maker)
    )
    dp.callback_query.middleware.register(
        SetAccessTokenMiddleware(async_session_maker)
    )
    dp.message.middleware.register(MediaMiddleware())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.getLogger('fast_bitrix24').addHandler(
        logging.StreamHandler()
    )
    asyncio.run(bot_start_polling())
