from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")  # "admin", "user", or "company"
    
    orders = relationship("Order", back_populates="user")
    locations = relationship("Location", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    address = Column(String)
    city = Column(String)
    postal_code = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="locations")
    orders = relationship("Order", back_populates="location")

class WaterCompany(Base):
    __tablename__ = "water_companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    contact_info = Column(String)
    rating = Column(Float, default=0.0)
    price_per_liter = Column(Float)
    
    offers = relationship("Offer", back_populates="company")

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("water_companies.id"))
    title = Column(String)
    description = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    volume = Column(Float)  # in liters
    
    company = relationship("WaterCompany", back_populates="offers")
    orders = relationship("Order", back_populates="offer")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    offer_id = Column(Integer, ForeignKey("offers.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    quantity = Column(Integer)  # number of containers
    total_price = Column(Float)
    is_delivery = Column(Boolean, default=True)  # True for delivery, False for pickup
    status = Column(String, default="pending")  # pending, confirmed, delivered
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
    offer = relationship("Offer", back_populates="orders")
    location = relationship("Location", back_populates="orders")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String)
    record_id = Column(Integer)
    action = Column(String)  # CREATE, UPDATE, DELETE
    old_values = Column(String, nullable=True)
    new_values = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs") 