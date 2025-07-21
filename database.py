from pymongo import MongoClient
from config import MONGO_URL, MONGO_DB_NAME


#todo: maybe change to AsyncClient
client = MongoClient(MONGO_URL)
db = client[MONGO_DB_NAME]

SURVEYS = 'surveys'
USERS = 'users'
EVENT_ORDERS = 'event_orders'
STATE_DATA = 'states_and_data'
ADVERTISING = 'advertising'


def get_collection(collection_name):
    return db[collection_name]


