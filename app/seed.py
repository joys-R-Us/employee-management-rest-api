import bcrypt
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, Department, Role


def hash_password(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("🌱 Starting database seeding...")

        # 1. Seed Admin
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(username="admin", password_hash=hash_password("password123"), role="admin")
            db.add(admin)
            print("✅ Admin user created.")

        # 2. Seed Departments (IDs 1, 2, 3, 4)
        depts = ["Information Technology", "Human Resources", "Finance", "Administration"]
        for name in depts:
            if not db.query(Department).filter(Department.name == name).first():
                db.add(Department(name=name, description=f"{name} Team"))
        db.flush()  # Pushes changes so IDs are generated
        print("✅ Departments seeded.")

        # 3. Seed Roles (IDs 1, 2, 3, 4)
        # We add these specifically so they match your JSON IDs
        roles_data = [
            {"id": 1, "title": "Software Engineer", "salary": 45000},
            {"id": 2, "title": "HR Manager", "salary": 55000},
            {"id": 3, "title": "Accountant", "salary": 40000},
            {"id": 4, "title": "System Administrator", "salary": 50000}
        ]

        for r in roles_data:
            if not db.query(Role).filter(Role.id == r["id"]).first():
                new_role = Role(id=r["id"], title=r["title"], base_salary=r["salary"])
                db.add(new_role)

        db.commit()
        print("✅ Roles seeded.")
        print("\n✨ Database is now ready for Sync!")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()