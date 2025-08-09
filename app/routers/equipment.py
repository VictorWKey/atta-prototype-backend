from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Equipment
from schemas import EquipmentCreate, EquipmentUpdate, EquipmentResponse
from routers.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[EquipmentResponse])
async def get_equipment(
    skip: int = 0,
    limit: int = 100,
    equipment_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all equipment with optional type filter."""
    query = db.query(Equipment)
    
    if equipment_type:
        query = query.filter(Equipment.type == equipment_type)
    
    equipment = query.offset(skip).limit(limit).all()
    return equipment

@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment_by_id(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get equipment by ID."""
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    return equipment

@router.post("/", response_model=EquipmentResponse)
async def create_equipment(
    equipment_data: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new equipment."""
    # Check if serial number already exists
    if db.query(Equipment).filter(Equipment.serial_number == equipment_data.serial_number).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Serial number already exists"
        )
    
    # Validate equipment type
    valid_types = ["Combustión", "Eléctrico", "Manual", "Otro"]
    if equipment_data.type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid equipment type. Must be one of: {', '.join(valid_types)}"
        )
    
    db_equipment = Equipment(
        type=equipment_data.type,
        brand=equipment_data.brand,
        model=equipment_data.model,
        serial_number=equipment_data.serial_number
    )
    
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    
    return db_equipment

@router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: int,
    equipment_data: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update equipment."""
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Check if serial number already exists (if being updated)
    if equipment_data.serial_number and equipment_data.serial_number != equipment.serial_number:
        if db.query(Equipment).filter(Equipment.serial_number == equipment_data.serial_number).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Serial number already exists"
            )
    
    # Validate equipment type
    if equipment_data.type:
        valid_types = ["Combustión", "Eléctrico", "Manual", "Otro"]
        if equipment_data.type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid equipment type. Must be one of: {', '.join(valid_types)}"
            )
    
    update_data = equipment_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(equipment, field, value)
    
    db.commit()
    db.refresh(equipment)
    
    return equipment

@router.delete("/{equipment_id}")
async def delete_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete equipment (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    db.delete(equipment)
    db.commit()
    
    return {"message": "Equipment deleted successfully"}

@router.get("/types/list")
async def get_equipment_types(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of equipment types."""
    return {
        "types": ["Combustión", "Eléctrico", "Manual", "Otro"]
    }
