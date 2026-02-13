from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


# ============================================================
# SOCIAL POSTS (Raw AI Inputs with Geo Location)
# ============================================================
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


# ============================================================
# PRODUCTS (Company + Model)
# ============================================================
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    model_name = Column(String, index=True)
    company = Column(String, index=True)

    current_price = Column(Float, default=0)

    # Relationships
    reviews = relationship("Review", back_populates="product", cascade="all, delete")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete")
    availability = relationship("Availability", back_populates="product", cascade="all, delete")


# ============================================================
# REVIEWS (Linked to Product + Location for Map Persistence)
# ============================================================
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, ForeignKey("products.id"))

    comment = Column(String)
    sentiment = Column(String, index=True)  # positive / negative / neutral
    confidence = Column(Float)

    # 🔥 NEW → Store location per review for persistent map
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    brand = Column(String, index=True)  # helps for brand color mapping

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="reviews")


# ============================================================
# PRICE HISTORY
# ============================================================
class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, ForeignKey("products.id"))
    month = Column(String)
    price = Column(Float)

    product = relationship("Product", back_populates="price_history")


# ============================================================
# AVAILABILITY
# ============================================================
class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, ForeignKey("products.id"))
    region = Column(String)
    available = Column(Boolean)

    product = relationship("Product", back_populates="availability")
