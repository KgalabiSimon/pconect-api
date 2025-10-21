from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
from app.db.models import Base, User, AdminUser
from app.db.database import engine, SessionLocal
from app.core.security import get_password_hash, generate_id

ADMIN_EMAIL = "admin@pconnect.com"
ADMIN_PASSWORD = "Admin2354"   # Using same password as in .env for testing
ADMIN_ROLE = "admin"

def init_db():
    print("Starting database initialization...")
    # 0) Quick connectivity check so failures are obvious
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError as e:
        print("❌ Database not reachable. Check connection settings (host, SSL, firewall) and try again.")
        print(f"Details: {e}")
        return

    # 1) Create tables (for dev/bootstrap; prefer Alembic migrations in prod)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return

    # 2) Seed admin user idempotently
    password_field = "password_hash" if hasattr(User, "password_hash") else (
        "hashed_password" if hasattr(User, "hashed_password") else None
    )
    if not password_field:
        print("❌ User model has no 'password_hash' or 'hashed_password' field.")
        return

    with SessionLocal() as db:
        try:
            admin = db.query(AdminUser).filter(AdminUser.email == ADMIN_EMAIL).first()
            if admin:
                print("ℹ️ Admin user already exists; nothing to do.")
                return

            # Ensure password is not too long for bcrypt
            safe_password = ADMIN_PASSWORD[:72] if len(ADMIN_PASSWORD) > 72 else ADMIN_PASSWORD
            hashed_password = get_password_hash(safe_password)
            print(f"Created password hash successfully")
            
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
            print("✅ Admin user created successfully")
        except IntegrityError as e:
            db.rollback()
            print(f"⚠️ Integrity error (likely duplicate): {e.orig}")
        except Exception as e:
            db.rollback()
            print(f"❌ Error creating admin user: {e}")

if __name__ == "__main__":
    print("Creating database tables and seeding admin...")
    init_db()
    print("Done.")
