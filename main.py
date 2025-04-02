import os
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

import uvicorn
import models
import schemas
import auth
from database import engine, get_db
from database_seed import seed_database
from database_management import drop_all_data
import json

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Seed the database
seed_database()

# Create FastAPI app with custom settings
app = FastAPI(
    title="Zamzam Water Service",
    description="API for ordering Zamzam water with delivery or pickup options",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Authentication routes
@app.post("/login", response_model=schemas.Token)
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User routes
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # # Log the user creation
    # log_audit(
    #     db=db,
    #     table_name="users",
    #     record_id=db_user.id,
    #     action="CREATE",
    #     new_values=json.dumps({"email": user.email, "username": user.username, "location": user.location}),
    #     user_id=db_user.id
    # )
    
    return db_user

# Location routes
@app.post("/locations/", response_model=schemas.Location)
def create_location(
    location: schemas.LocationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # If this is the first location or is_default is True, handle default location
    if location.is_default:
        # Remove default flag from other locations
        db.query(models.Location).filter(
            models.Location.user_id == current_user.id,
            models.Location.is_default == True
        ).update({"is_default": False})
    
    db_location = models.Location(
        **location.model_dump(),
        user_id=current_user.id
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@app.get("/locations/", response_model=List[schemas.Location])
def read_locations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    locations = db.query(models.Location).filter(
        models.Location.user_id == current_user.id
    ).all()
    return locations

@app.get("/locations/{location_id}", response_model=schemas.Location)
def read_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    location = db.query(models.Location).filter(
        models.Location.id == location_id,
        models.Location.user_id == current_user.id
    ).first()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

# Water Company routes
@app.get("/companies/", response_model=List[schemas.WaterCompany])
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = db.query(models.WaterCompany).offset(skip).limit(limit).all()
    return companies

# Offer routes
@app.get("/offers/", response_model=List[schemas.Offer])
def read_offers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    offers = db.query(models.Offer).offset(skip).limit(limit).all()
    return offers

@app.post("/companies/{company_id}/offers/", response_model=schemas.Offer)
def create_company_offer(
    company_id: int,
    offer: schemas.OfferCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify company exists
    company = db.query(models.WaterCompany).filter(models.WaterCompany.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Create the offer
    db_offer = models.Offer(
        **offer.model_dump(),
        company_id=company_id
    )
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer

@app.get("/companies/{company_id}/offers/", response_model=List[schemas.Offer])
def read_company_offers(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Verify company exists
    company = db.query(models.WaterCompany).filter(models.WaterCompany.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    offers = db.query(models.Offer).filter(
        models.Offer.company_id == company_id
    ).offset(skip).limit(limit).all()
    return offers

# Order routes
@app.post("/orders/", response_model=schemas.Order)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify offer exists
    offer = db.query(models.Offer).filter(models.Offer.id == order.offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Verify location exists and belongs to user
    location = db.query(models.Location).filter(
        models.Location.id == order.location_id,
        models.Location.user_id == current_user.id
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    total_price = offer.price * order.quantity
    db_order = models.Order(
        user_id=current_user.id,
        offer_id=order.offer_id,
        location_id=order.location_id,
        quantity=order.quantity,
        total_price=total_price,
        is_delivery=order.is_delivery
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # # Log the order creation
    # log_audit(
    #     db=db,
    #     table_name="orders",
    #     record_id=db_order.id,
    #     action="CREATE",
    #     new_values=json.dumps({
    #         "user_id": current_user.id,
    #         "offer_id": order.offer_id,
    #         "quantity": order.quantity,
    #         "total_price": total_price,
    #         "delivery_address": order.delivery_address,
    #         "is_delivery": order.is_delivery
    #     }),
    #     user_id=current_user.id
    # )
    
    return db_order

@app.get("/orders/", response_model=List[schemas.Order])
def read_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return orders

@app.get("/orders/{order_id}", response_model=schemas.Order)
def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.patch("/orders/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    order = db.query(models.Order).join(
        models.Offer
    ).filter(
        models.Order.id == order_id,
        models.Offer.company_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    db.refresh(order)
    return order

# Audit log routes
@app.get("/audit-logs/", response_model=List[dict])
def read_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Only admin can view audit logs
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view audit logs")
    
    logs = db.query(models.AuditLog).offset(skip).limit(limit).all()
    return logs

# Database Management routes
@app.post("/admin/drop-database", response_model=dict)
async def drop_database(current_user: models.User = Depends(auth.get_current_user)):
    # Only admin can drop database
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can perform this action"
        )
    
    try:
        result = drop_all_data()
        # Recreate tables and seed data
        models.Base.metadata.create_all(bind=engine)
        seed_database()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 
    
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Get PORT from environment or default to 8000
    uvicorn.run(app, host="0.0.1.1", port=port,reload=True)