from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_DETAILS, DATABASE_NAME

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client[DATABASE_NAME]

def get_database():
    return database

