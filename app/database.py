from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connection string for XAMPP MySQL (Username: root, Password: empty)
DATABASE_URL = "mysql+pymysql://root:@localhost/employee.db"

# The engine handles translating Python requests into raw SQL commands
engine = create_engine(DATABASE_URL)

# SessionLocal instances represent an active pipeline to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class used by models to maintain a catalog of database schemas
Base = declarative_base()

# Helper function to get a clean database session for API routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Safely closes the connection when the API request is finished