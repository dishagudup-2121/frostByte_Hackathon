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
<<<<<<< HEAD
    created_at: Optional[datetime] = None
=======
    created_at: Optional[datetime] = None
>>>>>>> 02680d5 (Add .gitignore and remove virtual environment)
