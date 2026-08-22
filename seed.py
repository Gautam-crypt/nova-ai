import os
import uuid
import json
from dotenv import load_dotenv
from jarvis.api.database import SessionLocal, engine
from jarvis.api.models import Base, User, Plan, PlanType, UserRole
from jarvis.api.auth import hash_password

load_dotenv()

# create tables if not exist
Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    
    # Plans
    plans = [
        Plan(
            id=str(uuid.uuid4()),
            name="Free",
            plan_type=PlanType.FREE,
            price_monthly=0,
            price_yearly=0,
            messages_per_day=50,
            memory_enabled=False,
            custom_personality=False,
            agents_enabled=json.dumps([])
        ),
        Plan(
            id=str(uuid.uuid4()),
            name="Pro",
            plan_type=PlanType.PRO,
            price_monthly=9.99,
            price_yearly=99.99,
            messages_per_day=500,
            memory_enabled=True,
            custom_personality=False,
            agents_enabled=json.dumps(["HERMES"])
        ),
        Plan(
            id=str(uuid.uuid4()),
            name="Enterprise",
            plan_type=PlanType.ENTERPRISE,
            price_monthly=49.99,
            price_yearly=499.99,
            messages_per_day=-1,
            memory_enabled=True,
            custom_personality=True,
            agents_enabled=json.dumps(["HERMES", "VISHWAKARMA", "DIVYA", "YAMA", "MANAS"])
        )
    ]
    
    if db.query(Plan).count() == 0:
        db.add_all(plans)
        db.commit()
        print("[SEED] Default plans created")
    else:
        print("[SEED] Plans already exist - skipping")

    # Admin
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_pass = os.getenv("ADMIN_PASSWORD")
    
    if admin_email and admin_pass:
        existing = db.query(User).filter(User.email == admin_email).first()
        if existing:
            print("[SEED] Admin already exists — skipping")
        else:
            free_plan = db.query(Plan).filter(Plan.plan_type == PlanType.ENTERPRISE).first()
            admin = User(
                id=str(uuid.uuid4()),
                email=admin_email,
                hashed_password=hash_password(admin_pass),
                full_name="Admin",
                role=UserRole.ADMIN,
                plan_id=free_plan.id if free_plan else None,
                nova_memory_collection=f"nova_admin_{uuid.uuid4().hex[:8]}"
            )
            db.add(admin)
            db.commit()
            print(f"[SEED] Admin created: {admin_email}")
    else:
        print("[SEED] No ADMIN_EMAIL or ADMIN_PASSWORD in .env")

    db.close()

if __name__ == "__main__":
    seed()
