import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Locate database relative to backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    db_path = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "water_quality.db"))
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    DATABASE_URL = f"sqlite:///{db_path}"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
