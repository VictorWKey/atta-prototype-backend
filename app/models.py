from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, jefe, operador
    position = Column(String)
    avatar = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    service_reports = relationship("ServiceReport", foreign_keys="ServiceReport.technician_id", back_populates="technician")
    created_reports = relationship("ServiceReport", foreign_keys="ServiceReport.created_by")

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contacts = relationship("Contact", back_populates="client")
    service_reports = relationship("ServiceReport", back_populates="client")

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    name = Column(String, nullable=False)
    position = Column(String)
    phone = Column(String)
    email = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="contacts")
    service_reports = relationship("ServiceReport", back_populates="requested_by")

class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # Combustión, Eléctrico, Manual, Otro
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    serial_number = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    service_reports = relationship("ServiceReport", back_populates="equipment")

class ServiceReport(Base):
    __tablename__ = "service_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(Integer, unique=True, nullable=False)
    date = Column(String, nullable=False)
    
    # Foreign Keys
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    requested_by_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Service Information
    service_type = Column(String, nullable=False)  # Preventivo, Correctivo, etc.
    billing_type = Column(String, nullable=False)  # Facturación, Renta, etc.
    
    # Readings
    battery_percentage = Column(Integer)
    horometer_readings = Column(JSON)  # {"h1": 1250, "h2": 1300, etc.}
    
    # Work Details
    work_performed = Column(Text)
    detected_damages = Column(Text)
    possible_causes = Column(JSON)  # [{"id": "1", "name": "Daño Operativo", "selected": true}]
    activities_performed = Column(Text)
    
    # Operation Points
    operation_points = Column(JSON)  # {"speed": 12, "auxiliaryFunctionsOperating": "Sí", etc.}
    
    # Inspection Items (usando JSONB para mejor performance en consultas)
    inspection_items = Column(JSON)  # [{"id": "1", "name": "Golpes deformaciones", "status": "OK", etc.}]
    
    # Comments and Parts
    technician_comments = Column(Text)
    applied_parts = Column(JSON)  # [{"description": "Aceite hidráulico", "quantity": 1}]
    
    # Work Time
    work_time = Column(JSON)  # {"date": "2025-01-01", "entryTime": "09:00", etc.}
    
    # Signatures and Status
    client_signature = Column(String)  # URL to signature image
    technician_signature = Column(String)  # URL to signature image
    status = Column(String, default="pending")  # pending, completed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    technician = relationship("User", foreign_keys=[technician_id], back_populates="service_reports")
    created_by_user = relationship("User", foreign_keys=[created_by])
    client = relationship("Client", back_populates="service_reports")
    requested_by = relationship("Contact", back_populates="service_reports")
    equipment = relationship("Equipment", back_populates="service_reports")
