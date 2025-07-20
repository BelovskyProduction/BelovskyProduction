from aiogram.dispatcher.router import Router

from handlers import router as conception_router
from advertising.handlers import advertising_router


base_router = Router()
base_router.include_router(conception_router)
base_router.include_router(advertising_router)

