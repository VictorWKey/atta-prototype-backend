from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

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
    work_performed: Optional[str] = None
    detected_damages: Optional[str] = None
    possible_causes: Optional[List[Dict[str, Any]]] = None
    activities_performed: Optional[str] = None
    operation_points: Optional[Dict[str, Any]] = None
    inspection_items: Optional[List[Dict[str, Any]]] = None
    technician_comments: Optional[str] = None
    applied_parts: Optional[List[Dict[str, Any]]] = None
    work_time: Optional[Dict[str, Any]] = None

class ServiceReportCreate(ServiceReportBase):
    client_id: int
    requested_by_id: int
    equipment_id: int

class ServiceReportUpdate(BaseModel):
    date: Optional[str] = None
    service_type: Optional[str] = None
    billing_type: Optional[str] = None
    battery_percentage: Optional[int] = None
    horometer_readings: Optional[Dict[str, Any]] = None
    work_performed: Optional[str] = None
    detected_damages: Optional[str] = None
    possible_causes: Optional[List[Dict[str, Any]]] = None
    activities_performed: Optional[str] = None
    operation_points: Optional[Dict[str, Any]] = None
    inspection_items: Optional[List[Dict[str, Any]]] = None
    technician_comments: Optional[str] = None
    applied_parts: Optional[List[Dict[str, Any]]] = None
    work_time: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    client_signature: Optional[str] = None
    technician_signature: Optional[str] = None

class ServiceReportResponse(ServiceReportBase):
    id: int
    report_number: int
    created_by: int
    client_id: int
    requested_by_id: int
    equipment_id: int
    technician_id: int
    status: str
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
