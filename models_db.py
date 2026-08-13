from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///defentra_siem.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SecurityEventModel(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String)  # e.g., "WAF_BLOCK", "ML_INTRUSION", "PHISHING_EMAIL"
    source_ip = Column(String, index=True)
    severity = Column(String)  # Low, Medium, High, Critical
    description = Column(String)
    confidence = Column(Float, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)
