from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.hive import HiveCreate, HiveResponse
from app.db.crud import create_hive, get_hives
from app.dependencies import get_db, get_current_user
from typing import List,Optional
import csv
from io import StringIO
from fastapi.responses import StreamingResponse
from datetime import date

router = APIRouter(tags=["hives"])

@router.post("/api/hives", response_model=HiveResponse, status_code=status.HTTP_201_CREATED)
async def create_hive_log(hive: HiveCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
    db_hive = await create_hive(db, hive)
    return db_hive

@router.get("/api/hives", response_model=List[HiveResponse])
async def read_hives(
    skip: int = 0,
    limit: int = 10,
    startDate: Optional[date] = Query(None, alias="start_date"),
    endDate: Optional[date] = Query(None, alias="end_date"),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    if startDate and endDate and startDate > endDate:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be after end date."
        )
    hives = await get_hives(db, skip=skip, limit=limit, startDate=startDate, endDate=endDate)
    return hives


@router.get("/api/hives/export", response_class=StreamingResponse)
async def export_hives_csv(skip: int = 0, limit: int = 100,     startDate: Optional[date] = Query(None, alias="start_date"),
    endDate: Optional[date] = Query(None, alias="end_date"), db=Depends(get_db), current_user=Depends(get_current_user)):

    if startDate and endDate and startDate > endDate:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be after end date."
        )
    hives = await get_hives(db, skip=skip, limit=limit, startDate=startDate, endDate=endDate)

    output = StringIO()
    csv_writer = csv.writer(output)

    csv_writer.writerow(["Hive ID", "Date Placed", "Latitude", "Longitude", "Number of Colonies", "Timestamp"])

    for hive in hives:
        csv_writer.writerow([hive["hiveId"], hive["datePlaced"], hive["latitude"], hive["longitude"], hive["numColonies"], hive["timestamp"]])

    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=hive_logs.csv"})
