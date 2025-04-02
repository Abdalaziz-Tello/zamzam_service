from sqlalchemy import text
from database import engine, SessionLocal

def drop_all_data():
    db = SessionLocal()
    try:
        # Disable foreign key checks
        db.execute(text("PRAGMA foreign_keys=OFF"))
        
        # Drop all tables
        db.execute(text("DROP TABLE IF EXISTS orders"))
        db.execute(text("DROP TABLE IF EXISTS offers"))
        db.execute(text("DROP TABLE IF EXISTS water_companies"))
        db.execute(text("DROP TABLE IF EXISTS locations"))
        db.execute(text("DROP TABLE IF EXISTS users"))
        db.execute(text("DROP TABLE IF EXISTS audit_logs"))
        
        # Re-enable foreign key checks
        db.execute(text("PRAGMA foreign_keys=ON"))
        
        db.commit()
        return {"message": "All data has been successfully dropped"}
    except Exception as e:
        db.rollback()
        raise Exception(f"Error dropping data: {str(e)}")
    finally:
        db.close() 