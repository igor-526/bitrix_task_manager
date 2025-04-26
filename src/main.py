import asyncio
from handlers import router as main_router
from create_bot import dp, bot
from middlewares import MediaMiddleware, AuthLogsMiddleware


async def bot_start_polling() -> None:
    dp.include_routers(main_router)
    dp.message.middleware.register(AuthLogsMiddleware())
    dp.callback_query.middleware.register(AuthLogsMiddleware())
    dp.message.middleware.register(MediaMiddleware())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(bot_start_polling())
