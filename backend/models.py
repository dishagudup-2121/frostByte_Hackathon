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

    brand = Column(String, index=True, nullable=False)
    text = Column(String, nullable=False)

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

    model_name = Column(String, index=True, nullable=False)
    company = Column(String, index=True, nullable=False)

    current_price = Column(Float, default=0)

    # 🔥 Relationships
    reviews = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    price_history = relationship(
        "PriceHistory",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    availability = relationship(
        "Availability",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


# ============================================================
# REVIEWS (Linked to Product + Location for Map + Company Insights)
# ============================================================
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    comment = Column(String, nullable=False)

    sentiment = Column(String, index=True)   # positive / negative / neutral
    confidence = Column(Float)

    # 🌍 Location (for review map endpoint)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)

    # 🚀 Important for company insights & fast aggregation
    brand = Column(String, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="reviews")


# ============================================================
# PRICE HISTORY (Optional - For trend charts)
# ============================================================
class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    month = Column(String)
    price = Column(Float)

    product = relationship("Product", back_populates="price_history")


# ============================================================
# AVAILABILITY (Optional - For regional analytics)
# ============================================================
class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    region = Column(String)
    available = Column(Boolean)

    product = relationship("Product", back_populates="availability")
