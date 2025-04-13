from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Annotated


class CropBase(BaseModel):
    name: str = Field(..., description="Name of the crop")
    floweringStart: date = Field(..., description="Start date of flowering (YYYY-MM-DD)")
    floweringEnd: date = Field(..., description="End date of flowering (YYYY-MM-DD)")
    latitude: Annotated[float, Field(ge=-90, le=90, description="Latitude of the crop location")]
    longitude: Annotated[float, Field(ge=-180, le=180, description="Longitude of the crop location")]
    recommendedHiveDensity: Annotated[int, Field(gt=0, description="Recommended number of hives per unit area")]

    @field_validator("floweringEnd")
    @classmethod
    def validate_flowering_dates(cls, v, info):
        values = info.data
        start = values.get("floweringStart")
        if start and v <= start:
            raise ValueError("floweringEnd must be after floweringStart")
        return v


class CropCreate(CropBase):
    pass


class CropResponse(CropBase):
    pass
