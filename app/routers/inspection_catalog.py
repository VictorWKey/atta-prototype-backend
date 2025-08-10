from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import InspectionCategory, InspectionItemTemplate, OperationPointTemplate
from schemas import (
    InspectionCategoryCreate, InspectionCategoryResponse,
    InspectionItemTemplateCreate, InspectionItemTemplateResponse,
    OperationPointTemplateCreate, OperationPointTemplateResponse
)
from routers.auth import get_current_active_user
from models import User

router = APIRouter()

# ============ INSPECTION CATEGORIES ============

@router.get("/categories", response_model=List[InspectionCategoryResponse])
async def get_inspection_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all inspection categories"""
    categories = db.query(InspectionCategory).filter(
        InspectionCategory.is_active == True
    ).order_by(InspectionCategory.order_index).all()
    return categories

@router.post("/categories", response_model=InspectionCategoryResponse)
async def create_inspection_category(
    category_data: InspectionCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new inspection category (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create categories"
        )
    
    # Check if category already exists
    existing = db.query(InspectionCategory).filter(
        InspectionCategory.name == category_data.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    category = InspectionCategory(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

# ============ INSPECTION ITEM TEMPLATES ============

@router.get("/categories/{category_id}/items", response_model=List[InspectionItemTemplateResponse])
async def get_inspection_items_by_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all inspection items for a specific category"""
    items = db.query(InspectionItemTemplate).filter(
        InspectionItemTemplate.category_id == category_id,
        InspectionItemTemplate.is_active == True
    ).order_by(InspectionItemTemplate.order_index).all()
    return items

@router.get("/items", response_model=List[InspectionItemTemplateResponse])
async def get_all_inspection_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all inspection items grouped by category"""
    items = db.query(InspectionItemTemplate).filter(
        InspectionItemTemplate.is_active == True
    ).order_by(
        InspectionItemTemplate.category_id,
        InspectionItemTemplate.order_index
    ).all()
    return items

@router.post("/items", response_model=InspectionItemTemplateResponse)
async def create_inspection_item(
    item_data: InspectionItemTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new inspection item (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create inspection items"
        )
    
    # Validate category exists
    category = db.query(InspectionCategory).filter(
        InspectionCategory.id == item_data.category_id
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    item = InspectionItemTemplate(**item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# ============ OPERATION POINT TEMPLATES ============

@router.get("/operation-points", response_model=List[OperationPointTemplateResponse])
async def get_operation_point_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all operation point templates"""
    templates = db.query(OperationPointTemplate).filter(
        OperationPointTemplate.is_active == True
    ).order_by(OperationPointTemplate.order_index).all()
    return templates

@router.post("/operation-points", response_model=OperationPointTemplateResponse)
async def create_operation_point_template(
    template_data: OperationPointTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new operation point template (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create operation point templates"
        )
    
    template = OperationPointTemplate(**template_data.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

# ============ COMBINED TEMPLATES FOR SERVICE REPORTS ============

@router.get("/templates/service-report")
async def get_service_report_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get combined templates for creating service reports"""
    
    # Get categories with their items
    categories = db.query(InspectionCategory).filter(
        InspectionCategory.is_active == True
    ).order_by(InspectionCategory.order_index).all()
    
    inspection_template = {}
    for category in categories:
        items = db.query(InspectionItemTemplate).filter(
            InspectionItemTemplate.category_id == category.id,
            InspectionItemTemplate.is_active == True
        ).order_by(InspectionItemTemplate.order_index).all()
        
        category_key = category.name.lower().replace(" ", "_")
        inspection_template[category_key] = [
            {
                "id": f"{category_key}_{item.id:03d}",
                "name": item.name,
                "category": category.name,
                "description": item.description
            }
            for item in items
        ]
    
    # Get operation points
    operation_points = db.query(OperationPointTemplate).filter(
        OperationPointTemplate.is_active == True
    ).order_by(OperationPointTemplate.order_index).all()
    
    operation_template = {}
    for op in operation_points:
        operation_template[op.name] = {
            "display_name": op.display_name,
            "field_type": op.field_type,
            "options": op.options,
            "validation_rules": op.validation_rules
        }
    
    return {
        "inspection_categories": inspection_template,
        "operation_points": operation_template,
        "status_options": {
            "OK": "Funcionando correctamente",
            "N/A": "No aplica",
            "R": "Requiere atención/reparación"
        }
    }
