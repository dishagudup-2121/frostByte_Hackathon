from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class SocialPostCreate(BaseModel):
    brand: str
    text: str
    latitude: float
    longitude: float
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    created_at: Optional[datetime] = None
