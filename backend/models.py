from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class SocialPost(Base):
    __tablename__ = "social_posts"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    text = Column(String)

    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)

    sentiment = Column(String, index=True)
    confidence = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
