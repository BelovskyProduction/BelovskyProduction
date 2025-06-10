import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

#todo: maybe change to AsyncClient
client = MongoClient(os.getenv('MONGO_URL'))
db = client[os.getenv('MONGO_DB_NAME')]

SURVEYS = 'surveys'
USERS = 'users'
EVENT_ORDERS = 'event_orders'
STATE_DATA = 'states_and_data'


def get_collection(collection_name):
    return db[collection_name]


