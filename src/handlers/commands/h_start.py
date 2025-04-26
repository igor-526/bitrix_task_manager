from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from funcs.menu import f_send_menu

router = Router(name=__name__)


@router.message(CommandStart())
async def h_command_start(message: types.Message,
                          state: FSMContext) -> None:
    await f_send_menu(message.from_user.id, state)
