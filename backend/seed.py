"""
Seed script to create initial users and sample data.
Run: python seed.py
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, engine, Base
from app.models import User, UserRole, Worker, Property
from app.auth import get_password_hash


def seed_database():
    """Create initial data in the database."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Database already seeded. Skipping...")
            return
        
        print("Seeding database...")
        
        # Create users
        admin = User(
            username="admin",
            email="admin@dclandscaping.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        
        worker = User(
            username="worker",
            email="worker@dclandscaping.com",
            hashed_password=get_password_hash("worker123"),
            role=UserRole.WORKER,
            is_active=True
        )
        db.add(worker)
        
        print("✓ Created users: admin, worker")
        
        # Create sample workers
        workers_data = [
            {"name": "Alex", "phone": "204-555-0101", "hourly_rate": 20.00},
            {"name": "Mike", "phone": "204-555-0102", "hourly_rate": 22.00},
            {"name": "John", "phone": "204-555-0103", "hourly_rate": 20.00},
        ]
        
        for w in workers_data:
            worker_obj = Worker(**w)
            db.add(worker_obj)
        
        print("✓ Created sample workers: Alex, Mike, John")
        
        # Create sample properties
        properties_data = [
            {"name": "Smith House", "address": "123 Main St"},
            {"name": "Johnson Residence", "address": "456 Oak Ave", "is_spring_cleanup": True},
            {"name": "City Park", "address": "789 Park Blvd", "is_fall_cleanup": True},
        ]
        
        for p in properties_data:
            property_obj = Property(**p)
            db.add(property_obj)
        
        print("✓ Created sample properties")
        
        db.commit()
        print("\n✅ Database seeded successfully!")
        print("\nLogin credentials:")
        print("  Admin:  admin / admin123")
        print("  Worker: worker / worker123")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
