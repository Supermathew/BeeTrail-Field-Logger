from app.db.database import get_database
from app.schemas.hive import HiveCreate
from app.schemas.crop import CropCreate
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash
from fastapi import HTTPException
from typing import List, Optional
import datetime

database = get_database()


def convert_dates_to_datetime(doc: dict):
    for key, value in doc.items():
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            doc[key] = datetime.datetime.combine(value, datetime.time())
    return doc


async def create_crop(db, crop: CropCreate):
    crop_collection = db["crops"]

    crop_dict = convert_dates_to_datetime(crop.dict())

    crop_dict["location"] = {
        "type": "Point",
        "coordinates": [crop_dict["longitude"], crop_dict["latitude"]]
    }

    await crop_collection.insert_one(crop_dict)
    return crop_dict


async def create_user(db, user: UserCreate):
    user_collection = db["users"]
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["password_hash"] = hashed_password
    del user_dict["password"]
    await user_collection.insert_one(user_dict)
    return user_dict

async def get_user_by_email(db, email: str, role: str = None):
    user_collection = db["users"]
    query = {"email": email}
    
    if role:
        query["role"] = role

    user = await user_collection.find_one(query)
    return user


async def create_hive(db, hive: HiveCreate):
    hive_collection = db["hives"]
    if await hive_collection.find_one({"hiveId": hive.hiveId}):
        raise HTTPException(status_code=400, detail="Hive ID already exists")
    hive_dict = convert_dates_to_datetime(hive.dict())
    hive_dict["timestamp"] = datetime.datetime.now(datetime.timezone.utc)
    await hive_collection.insert_one(hive_dict)
    return hive_dict


async def get_hives(
    db,
    skip: int = 0,
    limit: int = 10,
    startDate: Optional[datetime.date] = None,
    endDate: Optional[datetime.date] = None
):
    hive_collection = db["hives"]
    query = {}

    print(startDate)
    print(endDate)

    if startDate and endDate:
        if startDate and endDate:
            query["datePlaced"] = {
                "$gte": datetime.datetime.combine(startDate, datetime.time.min).replace(tzinfo=datetime.timezone.utc),
                "$lte": datetime.datetime.combine(endDate, datetime.time.max).replace(tzinfo=datetime.timezone.utc)
            }
    elif startDate:
        query["datePlaced"] = {"$gte": datetime.datetime.combine(startDate, datetime.time.min)}
    elif endDate:
        query["datePlaced"] = {"$lte": datetime.datetime.combine(endDate, datetime.time.max)}

    hives = await hive_collection.find(query).skip(skip).limit(limit).to_list(length=limit)
    return hives

import datetime
from bson.son import SON

import datetime

async def get_nearby_crops(db, latitude, longitude, radius, date):
    query_date = datetime.datetime.combine(date, datetime.time.min, tzinfo=datetime.timezone.utc)

    crop_collection = db.get_collection("crops")

    radius = radius * 1000


    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": radius
            }
        },
        "floweringStart": {"$lte": query_date},
        "floweringEnd": {"$gte": query_date}
    }

    crops = await crop_collection.find(query).to_list(length=None)
    return crops


async def get_user_sync_token(email: str):
    user = await database.users.find_one({"email": email})
    print(user)
    return user.get("sync_token") if user else None

async def update_user_sync_token(email: str):
    new_token = datetime.datetime.utcnow().timestamp()
    await database.users.update_one({"email": email}, {"$set": {"sync_token": new_token}})
    return new_token

async def get_changes_since_sync(collection_name: str, sync_token: float):
    collection = database[collection_name]
    return await collection.find({"lastModified": {"$gt": sync_token}}).to_list(length=None)