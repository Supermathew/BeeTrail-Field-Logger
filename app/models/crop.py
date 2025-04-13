from typing import List, Literal
from pydantic import BaseModel, Field
from datetime import date

class GeoPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float]

class Crop(BaseModel):
    name: str
    floweringStart: date
    floweringEnd: date
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    recommendedHiveDensity: int = Field(..., gt=0)
