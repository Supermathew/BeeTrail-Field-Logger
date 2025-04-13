from pydantic import BaseModel, Field
from datetime import date, datetime,timezone

class Hive(BaseModel):
    hiveId: str = Field(..., description="Unique identifier for the hive")
    datePlaced: date = Field(..., description="Date the hive was placed (YYYY-MM-DD)")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of the hive")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of the hive")
    numColonies: int = Field(..., gt=0, description="Number of bee colonies in the hive")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
