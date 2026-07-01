from app.models.tables import User,UserRole
from app.core.security import hash_password
from app.models.dataConfig import get_db
from sqlalchemy.orm import Session

def seed_admin(db: Session):
    # Check if the admin user already exists
    existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if existing_admin:
        print("Admin user already exists.")
        return
    # if not then create the admin User
    admin_user = User(
        full_name="Admin User",
        email="admin@gmail.com",
        phone="1234567890",
        password_hash=hash_password("admin"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    print("Admin user created successfully.")
