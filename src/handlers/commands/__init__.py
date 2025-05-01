__all__ = ("router", )

from aiogram import Router

from .h_menu import router as router_menu
from .h_start import router as router_start

router = Router()
router.include_routers(router_start, router_menu)
