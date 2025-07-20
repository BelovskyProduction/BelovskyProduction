import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.mongo import MongoStorage

from config import BOT_TOKEN, MONGO_URL, MONGO_DB_NAME
from routers import base_router
from service import clear_pending_conception_generation


def get_mongo_storage():
    return MongoStorage.from_url(url=MONGO_URL, db_name=MONGO_DB_NAME)


async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = get_mongo_storage()
    dp = Dispatcher(storage=storage)
    dp.include_router(base_router)
    await clear_pending_conception_generation(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", filename='logs.log',
                        filemode='a')
    print('bot started')
    asyncio.run(main())
