from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class LocationBase(BaseModel):
    name: str
    address: str
    city: str
    postal_code: str
    latitude: float
    longitude: float
    is_default: bool = False

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    username: str
    role: str = "user"  # "admin", "user", or "company"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    locations: List[Location] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class WaterCompanyBase(BaseModel):
    name: str
    description: str
    contact_info: str
    rating: float = 0.0
    price_per_liter: float

class WaterCompanyCreate(WaterCompanyBase):
    pass

class WaterCompany(WaterCompanyBase):
    id: int

    class Config:
        from_attributes = True

class OfferBase(BaseModel):
    title: str
    description: str
    price: float
    quantity: int
    volume: float

class OfferCreate(OfferBase):
    company_id: int

class Offer(OfferBase):
    id: int
    company_id: int
    company: WaterCompany

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    offer_id: int
    location_id: int
    quantity: int
    is_delivery: bool = True

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    offer: Offer
    location: Location

    class Config:
        from_attributes = True 