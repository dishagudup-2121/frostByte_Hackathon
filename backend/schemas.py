from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SocialPostCreate(BaseModel):
    brand: str
    text: str
    latitude: float
    longitude: float
    sentiment: str
    confidence: float
    created_at: Optional[datetime] = None