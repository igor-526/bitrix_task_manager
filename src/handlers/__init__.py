__all__ = ("router", )

from aiogram import Router

from .commands import router as router_commands
from .tasks import router as router_tasks


router = Router()
router.include_routers(router_commands, router_tasks)
