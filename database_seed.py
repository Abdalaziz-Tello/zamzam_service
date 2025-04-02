from sqlalchemy.orm import Session
from database import SessionLocal
import models
import auth

def seed_database():
    db = SessionLocal()
    try:
        # Create admin user if not exists
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            admin = models.User(
                email="admin@zamzam.com",
                username="admin",
                hashed_password=auth.get_password_hash("admin123"),
                is_active=True
            )
            db.add(admin)
            db.commit()

        # Create water companies if not exist
        companies = [
            {
                "name": "Zamzam Water Co.",
                "description": "Premium Zamzam water supplier",
                "contact_info": "+966 50 123 4567",
                "rating": 4.8,
                "price_per_liter": 5.0
            },
            {
                "name": "Holy Water Services",
                "description": "Trusted Zamzam water provider",
                "contact_info": "+966 50 987 6543",
                "rating": 4.5,
                "price_per_liter": 4.5
            },
            {
                "name": "Makkah Water Solutions",
                "description": "Quality Zamzam water delivery",
                "contact_info": "+966 50 456 7890",
                "rating": 4.2,
                "price_per_liter": 4.0
            }
        ]
        
        for company_data in companies:
            company = db.query(models.WaterCompany).filter(
                models.WaterCompany.name == company_data["name"]
            ).first()
            if not company:
                company = models.WaterCompany(**company_data)
                db.add(company)
        
        db.commit()

        # Create offers if not exist
        offers = [
            {
                "company_id": 1,  # Zamzam Water Co.
                "title": "5L Premium Zamzam",
                "description": "5 liter container of premium Zamzam water",
                "price": 25.0,
                "quantity": 1,
                "volume": 5.0
            },
            {
                "company_id": 1,
                "title": "10L Family Pack",
                "description": "10 liter container of premium Zamzam water",
                "price": 45.0,
                "quantity": 1,
                "volume": 10.0
            },
            {
                "company_id": 2,  # Holy Water Services
                "title": "5L Standard Zamzam",
                "description": "5 liter container of standard Zamzam water",
                "price": 22.5,
                "quantity": 1,
                "volume": 5.0
            },
            {
                "company_id": 2,
                "title": "Bulk Order - 50L",
                "description": "50 liter bulk order of Zamzam water",
                "price": 200.0,
                "quantity": 1,
                "volume": 50.0
            },
            {
                "company_id": 3,  # Makkah Water Solutions
                "title": "5L Economy Pack",
                "description": "5 liter container of economy Zamzam water",
                "price": 20.0,
                "quantity": 1,
                "volume": 5.0
            },
            {
                "company_id": 3,
                "title": "20L Business Pack",
                "description": "20 liter container of Zamzam water for businesses",
                "price": 75.0,
                "quantity": 1,
                "volume": 20.0
            }
        ]
        
        for offer_data in offers:
            offer = db.query(models.Offer).filter(
                models.Offer.company_id == offer_data["company_id"],
                models.Offer.title == offer_data["title"]
            ).first()
            if not offer:
                offer = models.Offer(**offer_data)
                db.add(offer)
        
        db.commit()

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close() 