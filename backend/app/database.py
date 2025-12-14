import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Debug - print all env vars
print("=== Environment Variables ===")
for key, value in os.environ.items():
    if "MYSQL" in key or "DATABASE" in key:
        print(f"{key}: {value[:20]}...")
print("=== End ===")

DATABASE_URL = os.environ.get("DATABASE_URL", "")

print(f"DATABASE_URL from env: {DATABASE_URL[:50] if DATABASE_URL else 'EMPTY'}")

# Fix mysql:// to mysql+pymysql://
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

if not DATABASE_URL:
    DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/railway"

print(f"Final DATABASE_URL: {DATABASE_URL[:50]}")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()