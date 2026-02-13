from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
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


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, index=True)
    company = Column(String, index=True)
    current_price = Column(Float)

    reviews = relationship("Review", back_populates="product")
    price_history = relationship("PriceHistory", back_populates="product")
    availability = relationship("Availability", back_populates="product")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    comment = Column(String)
    sentiment = Column(String, index=True)  # positive / negative
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="reviews")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    month = Column(String)
    price = Column(Float)

    product = relationship("Product", back_populates="price_history")


class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    region = Column(String)
    available = Column(Boolean)

    product = relationship("Product", back_populates="availability")
