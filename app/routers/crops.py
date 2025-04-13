from fastapi import APIRouter, Depends, status, Query
from app.schemas.crop import CropCreate, CropResponse
from app.db.crud import create_crop, get_nearby_crops
from app.dependencies import get_db, get_current_user
from typing import List
from datetime import date

router = APIRouter(tags=["crops"])

@router.post("/api/crops", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
async def create_crop_log(crop: CropCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
    db_crop = await create_crop(db, crop)
    return db_crop

@router.get("/api/crops/nearby", response_model=List[CropResponse])
async def get_nearby_crops_endpoint(latitude: float = Query(..., ge=-90, le=90), longitude: float = Query(..., ge=-180, le=180), radius: float = Query(100, gt=0), date: date = Query(date.today()), db=Depends(get_db), current_user=Depends(get_current_user)):
    crops = await get_nearby_crops(db, latitude, longitude, radius, date)
    return crops
