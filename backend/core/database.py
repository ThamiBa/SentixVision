from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Equipment(Base):
    __tablename__ = 'equipment'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)  # Sewing Machine, Cutting Table, etc.
    status = Column(String, default="Operational")  # Operational, Maintenance, Offline
    last_service = Column(DateTime, default=datetime.utcnow)
    next_service = Column(DateTime)
    
    maintenance_records = relationship("MaintenanceLog", back_populates="equipment")

class MaintenanceLog(Base):
    __tablename__ = 'maintenance_logs'
    
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'))
    action = Column(String)
    perfomed_by = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String)
    
    equipment = relationship("Equipment", back_populates="maintenance_records")

class SystemConfig(Base):
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database Setup
DATABASE_URL = "sqlite:///./sentix_vision.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Seed data if empty
    db = SessionLocal()
    if db.query(Equipment).count() == 0:
        machines = [
            Equipment(name="Juki DDL-8700", type="Sewing Machine", status="Operational"),
            Equipment(name="Brother S-7100A", type="Sewing Machine", status="Operational"),
            Equipment(name="Gerber Paragon", type="Cutting Machine", status="Operational")
        ]
        db.add_all(machines)
        db.commit()
    db.close()
