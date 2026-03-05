from backend.database.database import engine, Base
from backend.models.models import Tenant, User, Camera
from backend.api.auth import get_password_hash

import time
from sqlalchemy.exc import OperationalError

def init_db():
    print("[InitDB] Attempting to connect to database...")
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            print("[InitDB] Tables created.")
            break
        except OperationalError as e:
            retries -= 1
            print(f"[InitDB] Database not ready. Retrying in 5 seconds... ({retries} retries left)")
            time.sleep(5)
    
    if retries == 0:
        print("[InitDB] FAILED to connect to database after multiple retries.")
        return

    # Optional: Add seed data
    # (In Production, this would be handled by migrations/seed scripts)
    from sqlalchemy.orm import Session
    from backend.database.database import SessionLocal

    db = SessionLocal()
    try:
        # Check if we already have a tenant
        if db.query(Tenant).count() == 0:
            print("[InitDB] Seeding initial data...")
            # 1. Create Tenant
            tenant = Tenant(name="Maison Sentix", subscription_plan="Enterprise")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)

            # 2. Create Admin User
            admin = User(
                email="admin@sentix.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Chief Artisan",
                role="Admin",
                tenant_id=tenant.id
            )
            db.add(admin)

            # 3. Create Default Camera
            camera = Camera(
                name="Atelier Main",
                url="0", # Default webcam
                location="Main Floor",
                tenant_id=tenant.id
            )
            db.add(camera)
            
            db.commit()
            print("[InitDB] Seeding complete.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
