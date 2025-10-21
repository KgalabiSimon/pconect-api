from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
# Import all models so they are registered with Base.metadata
from app.db.models import (
    Base, User, AdminUser, SecurityOfficer, 
    Visitor, Building, Floor, Block, 
    Space, Booking, CheckIn, LaptopRecord
)
from app.db.database import engine, SessionLocal
from app.core.security import get_password_hash, generate_id

ADMIN_EMAIL = "admin@pconnect.com"
ADMIN_PASSWORD = "Admin2354"   # Using same password as in .env for testing
ADMIN_ROLE = "admin"

def init_db():
    print("Initializing database...")
    
    try:
        print("1. Creating all tables...")
        # This will create all tables for all models imported above
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully:")
        # List all tables that were created
        table_names = Base.metadata.tables.keys()
        for table in table_names:
            print(f"  - {table}")
        
        print("\n2. Creating admin user...")
        with SessionLocal() as db:
            # Check if admin already exists
            admin = db.query(AdminUser).filter(AdminUser.email == ADMIN_EMAIL).first()
            if admin:
                print("ℹ️ Admin user already exists")
                return
            
            # Create new admin user
            hashed_password = get_password_hash(ADMIN_PASSWORD)
            admin_user = AdminUser(
                id=generate_id("ADM", 1),  # First admin
                email=ADMIN_EMAIL,
                first_name="Admin",
                last_name="User",
                role="admin",
                is_active=True,
                hashed_password=hashed_password
            )
            
            db.add(admin_user)
            db.commit()
            print(f"✅ Admin user created successfully")
            print(f"Email: {ADMIN_EMAIL}")
            print(f"Password: {ADMIN_PASSWORD}")  # Only show in development
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    init_db()
