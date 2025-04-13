from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class SyncRequest(BaseModel):
    syncToken: float
    changes: Optional[List[Dict[str, Any]]] = None

class SyncTokenResponse(BaseModel):
    syncToken: float

class SyncDataResponse(BaseModel):
    syncToken: float
    changes: List[Dict[str, Any]]