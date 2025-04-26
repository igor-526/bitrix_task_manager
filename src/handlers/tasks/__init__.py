__all__ = ("router", )

from aiogram import Router
from .h_tasks import router as router_tasks
from .h_tasks_change_created_by import (
    router as router_tasks_change_created_by)
from .h_tasks_change_responsible import (
    router as router_tasks_change_responsible)
from .h_tasks_change_deadline import (
    router as router_tasks_change_deadline)

router = Router()
router.include_routers(router_tasks,
                       router_tasks_change_created_by,
                       router_tasks_change_responsible,
                       router_tasks_change_deadline)
