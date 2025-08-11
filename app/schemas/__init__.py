from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

# Enums for Inspection and Operation Points
class InspectionStatus(str, Enum):
    """Status values for inspection items"""
    OK = "OK"
    NA = "N/A"
    R = "R"  # Requiere atención/reparación

class OperationPointStatus(str, Enum):
    """Status values for operation points"""
    SI = "SÍ"
    NO = "NO"
    NA = "N/A"

class InspectionCategory(str, Enum):
    """Categories for inspection items"""
    ESTRUCTURAL = "ESTRUCTURAL"
    RUEDAS = "RUEDAS"
    SEGURIDAD = "SEGURIDAD"
    FUNCIONALES = "FUNCIONALES"
    FUGAS_DE_ACEITE = "FUGAS DE ACEITE"
    # Allow backwards compatibility with sample data
    estructural = "ESTRUCTURAL"
    ruedas = "RUEDAS"
    seguridad = "SEGURIDAD"
    funcionales = "FUNCIONALES"
    fugas_de_aceite = "FUGAS DE ACEITE"

# Structured schemas for Operation Points
class OperationPoints(BaseModel):
    """Puntos de Operación - Structured model based on the form"""
    # Velocidad de avance
    velocidad_avance: Optional[int] = Field(None, description="Velocidad de avance en Km/h", ge=0, le=50)
    
    # Funciones auxiliares operando (SÍ/NO/N/A)
    funciones_auxiliares_operando: Optional[OperationPointStatus] = Field(None, description="Funciones auxiliares operando")
    
    # Paro de emergencia dentro de especificaciones (SÍ/NO/N/A)  
    paro_emergencia_especificaciones: Optional[OperationPointStatus] = Field(None, description="Paro de emergencia dentro de especificaciones")
    
    # Campos adicionales del documento PDF
    sistema: Optional[str] = Field(None, description="Sistema general")
    objeto_inspeccion: Optional[str] = Field(None, description="Objeto de inspección")

# Equipment Specifications (from PDF form)
class EquipmentSpecifications(BaseModel):
    """Especificaciones adicionales del equipo"""
    model_config = {"protected_namespaces": ()}
    
    model_year: Optional[str] = Field(None, description="Año del modelo")
    capacity: Optional[str] = Field(None, description="Capacidad (ej: 1.5 ton)")
    fuel_type: Optional[str] = Field(None, description="Tipo de combustible")
    additional_specs: Optional[Dict[str, str]] = Field(None, description="Especificaciones adicionales")

# Applied Parts and Consumables (from PDF)
class AppliedPart(BaseModel):
    """Refacciones y consumibles aplicados"""
    type: Literal["refacciones", "consumibles"] = Field(..., description="Tipo de parte")
    description: str = Field(..., description="Descripción de la parte")
    quantity: str = Field(..., description="Cantidad (puede ser número o medida como '2L')")

# Detailed Work Time (from PDF)
class WorkTime(BaseModel):
    """Tiempo de mano de obra detallado"""
    fecha: str = Field(..., description="Fecha del trabajo")
    hora_entrada: str = Field(..., description="Hora de entrada")
    hora_salida: str = Field(..., description="Hora de salida")
    total_horas: float = Field(..., description="Total de horas trabajadas", ge=0)
    tiempo_extra: Optional[float] = Field(0, description="Tiempo extra en horas", ge=0)

# Multiple Signatures Support
class Signature(BaseModel):
    """Firma individual"""
    name: str = Field(..., description="Nombre del firmante")
    signature_url: str = Field(..., description="URL de la imagen de la firma")
    timestamp: str = Field(..., description="Timestamp de la firma")

class Signatures(BaseModel):
    """Sistema de múltiples firmas"""
    client: Optional[Signature] = Field(None, description="Firma del cliente")
    technician: Optional[Signature] = Field(None, description="Firma del técnico")
    supervisor: Optional[Signature] = Field(None, description="Firma del supervisor")

class InspectionItem(BaseModel):
    """Single inspection item with category and status"""
    id: str = Field(..., description="Unique identifier for the inspection item")
    name: str = Field(..., description="Name of the inspection item")
    category: str = Field(..., description="Category of the inspection")  # Changed to str for flexibility
    status: InspectionStatus = Field(..., description="Status of the inspection item")
    notes: Optional[str] = Field(None, description="Additional notes for this item")

# Inspection Category for structured inspection
class InspectionCategoryGroup(BaseModel):
    """Grupo de inspección por categoría"""
    category: str = Field(..., description="Nombre de la categoría")
    items: List[InspectionItem] = Field(..., description="Items de inspección en esta categoría")

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str  # admin, jefe, operador
    position: Optional[str] = None
    avatar: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    position: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Contact Schemas
class ContactBase(BaseModel):
    name: str
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class ContactCreate(ContactBase):
    client_id: int

class ContactUpdate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: int
    client_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Client Schemas
class ClientBase(BaseModel):
    name: str
    address: str

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    contacts: List[ContactResponse] = []
    
    class Config:
        from_attributes = True

# Equipment Schemas
class EquipmentBase(BaseModel):
    type: str  # Combustión, Eléctrico, Manual, Otro
    brand: str
    model: str
    serial_number: str

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(EquipmentBase):
    pass

class EquipmentResponse(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Service Report Schemas
class ServiceReportBase(BaseModel):
    date: str
    service_type: str
    billing_type: str
    battery_percentage: Optional[int] = None
    horometer_readings: Dict[str, Any]
    equipment_specifications: Optional[EquipmentSpecifications] = None
    work_performed: Optional[str] = None
    detected_damages: Optional[str] = None
    possible_causes: Optional[List[Dict[str, Any]]] = None
    activities_performed: Optional[str] = None
    operation_points: Optional[OperationPoints] = None
    inspection_items: Optional[List[InspectionCategoryGroup]] = None
    technician_comments: Optional[str] = None
    client_observations: Optional[str] = None
    applied_parts: Optional[List[AppliedPart]] = None
    work_time: Optional[WorkTime] = None
    signatures: Optional[Signatures] = None

class ServiceReportCreate(ServiceReportBase):
    client_id: int
    requested_by_id: int
    equipment_id: int
    status: Optional[str] = "pending"
    pending_reason: Optional[str] = None

class ServiceReportUpdate(BaseModel):
    date: Optional[str] = None
    service_type: Optional[str] = None
    billing_type: Optional[str] = None
    battery_percentage: Optional[int] = None
    horometer_readings: Optional[Dict[str, Any]] = None
    equipment_specifications: Optional[EquipmentSpecifications] = None
    work_performed: Optional[str] = None
    detected_damages: Optional[str] = None
    possible_causes: Optional[List[Dict[str, Any]]] = None
    activities_performed: Optional[str] = None
    operation_points: Optional[OperationPoints] = None
    inspection_items: Optional[List[InspectionCategoryGroup]] = None
    technician_comments: Optional[str] = None
    client_observations: Optional[str] = None
    applied_parts: Optional[List[AppliedPart]] = None
    work_time: Optional[WorkTime] = None
    signatures: Optional[Signatures] = None
    status: Optional[str] = None
    pending_reason: Optional[str] = None
    client_signature: Optional[str] = None
    technician_signature: Optional[str] = None

class ServiceReportResponse(ServiceReportBase):
    id: int
    created_by: int
    client_id: int
    requested_by_id: int
    equipment_id: int
    technician_id: int
    status: str
    pending_reason: Optional[str] = None
    client_signature: Optional[str] = None
    technician_signature: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested relationships
    technician: UserResponse
    client: ClientResponse
    requested_by: ContactResponse
    equipment: EquipmentResponse
    
    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Inspection Catalog Schemas
class InspectionCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    order_index: Optional[int] = 0

class InspectionCategoryCreate(InspectionCategoryBase):
    pass

class InspectionCategoryResponse(InspectionCategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class InspectionItemTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    order_index: Optional[int] = 0

class InspectionItemTemplateCreate(InspectionItemTemplateBase):
    category_id: int

class InspectionItemTemplateResponse(InspectionItemTemplateBase):
    id: int
    category_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class OperationPointTemplateBase(BaseModel):
    name: str
    display_name: str
    field_type: str  # number, select, boolean
    options: Optional[List[str]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    order_index: Optional[int] = 0

class OperationPointTemplateCreate(OperationPointTemplateBase):
    pass

class OperationPointTemplateResponse(OperationPointTemplateBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
