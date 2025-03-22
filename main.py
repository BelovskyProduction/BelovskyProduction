import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.mongo import MongoStorage
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import router


def get_mongo_storage():
    return MongoStorage.from_url(url=os.getenv('MONGO_URL'), db_name=os.getenv('MONGO_DB_NAME'))


async def main():
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    storage = get_mongo_storage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())
