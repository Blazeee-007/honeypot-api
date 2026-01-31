from sqlalchemy import create_engine, Column, String, Boolean, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(String, primary_key=True, index=True) # conversation_id
    timestamp = Column(DateTime, default=datetime.utcnow)
    incoming_message = Column(String)
    response_text = Column(String)
    is_scam = Column(Boolean)
    upi_ids = Column(JSON) # List of strings
    bank_accounts = Column(JSON)
    phishing_links = Column(JSON)
    suggested_delay = Column(Float)
    metadata_json = Column(JSON)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
