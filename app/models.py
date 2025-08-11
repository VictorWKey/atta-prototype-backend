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
    created_reports = relationship("ServiceReport", foreign_keys="ServiceReport.created_by", overlaps="created_by_user")

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
    horometer_readings = Column(JSON)  # {"h1": 1250, "h2": 1300, "h3": 850, etc.}
    
    # Equipment Specifications (from PDF form)
    equipment_specifications = Column(JSON)  # {"model_year": "2025", "capacity": "1.5 ton", etc.}
    
    # Work Details
    work_performed = Column(Text)
    detected_damages = Column(Text)
    possible_causes = Column(JSON)  # [{"id": "1", "name": "Daño Operativo", "selected": true}]
    activities_performed = Column(Text)
    
    # Operation Points (expanded from PDF)
    operation_points = Column(JSON)  # {
    #   "velocidad_avance": 12,
    #   "funciones_auxiliares_operando": "SÍ", 
    #   "paro_emergencia_especificaciones": "SÍ",
    #   "sistema": "OK",
    #   "objeto_inspeccion": "montacargas"
    # }
    
    # Detailed Inspection Items (from PDF checklist)
    inspection_items = Column(JSON)  # [
    #   {
    #     "category": "ESTRUCTURAL",
    #     "items": [
    #       {"name": "GOLPES DEFORMACIONES", "status": "OK", "notes": ""},
    #       {"name": "SOLDADURA FISURADAS", "status": "N/A", "notes": ""},
    #       {"name": "PARTES SUELTAS/FRACTURADAS", "status": "R", "notes": "Revisar"}
    #     ]
    #   },
    #   {
    #     "category": "RUEDAS", 
    #     "items": [...]
    #   }
    # ]
    
    # Applied Parts and Consumables (from PDF)
    applied_parts = Column(JSON)  # [
    #   {"type": "refacciones", "description": "Espejo retrovisor", "quantity": 1},
    #   {"type": "consumibles", "description": "Aceite hidráulico", "quantity": "2L"}
    # ]
    
    # Detailed Work Time (from PDF)
    work_time = Column(JSON)  # {
    #   "fecha": "08/07/25",
    #   "hora_entrada": "9:00 AM", 
    #   "hora_salida": "10:30 AM",
    #   "total_horas": 1.5,
    #   "tiempo_extra": 0
    # }
    
    # Comments and Additional Info
    technician_comments = Column(Text)
    client_observations = Column(Text)  # Observaciones del cliente
    
    # Multiple Signatures (from PDF)
    signatures = Column(JSON)  # {
    #   "client": {"name": "Roberto", "signature_url": "...", "timestamp": "..."},
    #   "technician": {"name": "Juan Pérez", "signature_url": "...", "timestamp": "..."},
    #   "supervisor": {"name": "...", "signature_url": "...", "timestamp": "..."}
    # }
    
    # Legacy signature fields (mantener compatibilidad)
    client_signature = Column(String)  # URL to signature image
    technician_signature = Column(String)  # URL to signature image
    status = Column(String, default="pending")  # pending, completed
    pending_reason = Column(Text)  # Razón por la cual el reporte está pendiente
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    technician = relationship("User", foreign_keys=[technician_id], back_populates="service_reports")
    created_by_user = relationship("User", foreign_keys=[created_by], overlaps="created_reports")
    client = relationship("Client", back_populates="service_reports")
    requested_by = relationship("Contact", back_populates="service_reports")
    equipment = relationship("Equipment", back_populates="service_reports")

# Inspection Catalog Models
class InspectionCategory(Base):
    __tablename__ = "inspection_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # ESTRUCTURAL, RUEDAS, etc.
    description = Column(String)
    order_index = Column(Integer, default=0)  # Para ordenar en la UI
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    inspection_items = relationship("InspectionItemTemplate", back_populates="category")

class InspectionItemTemplate(Base):
    __tablename__ = "inspection_item_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("inspection_categories.id"), nullable=False)
    name = Column(String, nullable=False)  # GOLPES DEFORMACIONES, etc.
    description = Column(String)
    order_index = Column(Integer, default=0)  # Para ordenar dentro de la categoría
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("InspectionCategory", back_populates="inspection_items")

class OperationPointTemplate(Base):
    __tablename__ = "operation_point_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # velocidad_avance, funciones_auxiliares_operando, etc.
    display_name = Column(String, nullable=False)  # "Velocidad de avance", etc.
    field_type = Column(String, nullable=False)  # number, select, boolean
    options = Column(JSON)  # Para campos select: ["SÍ", "NO", "N/A"]
    validation_rules = Column(JSON)  # min, max, required, etc.
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
