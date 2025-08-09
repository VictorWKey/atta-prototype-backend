from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import os
import uuid

from database import get_db
from models import User, ServiceReport, Client, Contact, Equipment
from schemas import ServiceReportCreate, ServiceReportUpdate, ServiceReportResponse
from routers.auth import get_current_active_user
from core.config import settings
from utils.pdf_generator import generate_service_report_pdf
from fastapi.responses import Response

router = APIRouter()

def get_next_report_number(db: Session) -> int:
    """Get the next report number."""
    last_report = db.query(ServiceReport).order_by(desc(ServiceReport.report_number)).first()
    if last_report:
        return last_report.report_number + 1
    return 1001  # Start from 1001

@router.get("/", response_model=List[ServiceReportResponse])
async def get_service_reports(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    client_id: Optional[int] = None,
    technician_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get service reports with filters."""
    query = db.query(ServiceReport)
    
    # Role-based filtering
    if current_user.role == "operador":
        # Operators can only see their own reports
        query = query.filter(ServiceReport.technician_id == current_user.id)
    
    # Apply filters
    if status_filter:
        query = query.filter(ServiceReport.status == status_filter)
    
    if client_id:
        query = query.filter(ServiceReport.client_id == client_id)
    
    if technician_id and current_user.role in ["admin", "jefe"]:
        query = query.filter(ServiceReport.technician_id == technician_id)
    
    # Order by report number descending
    reports = query.order_by(desc(ServiceReport.report_number)).offset(skip).limit(limit).all()
    return reports

@router.get("/{report_id}", response_model=ServiceReportResponse)
async def get_service_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get service report by ID."""
    report = db.query(ServiceReport).filter(ServiceReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service report not found"
        )
    
    # Role-based access control
    if current_user.role == "operador" and report.technician_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return report

@router.post("/", response_model=ServiceReportResponse)
async def create_service_report(
    report_data: ServiceReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new service report."""
    # Validate client exists
    client = db.query(Client).filter(Client.id == report_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Validate contact exists and belongs to client
    contact = db.query(Contact).filter(
        Contact.id == report_data.requested_by_id,
        Contact.client_id == report_data.client_id
    ).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found or doesn't belong to the specified client"
        )
    
    # Validate equipment exists
    equipment = db.query(Equipment).filter(Equipment.id == report_data.equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    # Validate service type
    valid_service_types = ["Preventivo", "Correctivo", "Instalación", "Reparación", "Otro"]
    if report_data.service_type not in valid_service_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid service type. Must be one of: {', '.join(valid_service_types)}"
        )
    
    # Validate billing type
    valid_billing_types = ["Facturación", "Renta", "Garantía", "Sin costo"]
    if report_data.billing_type not in valid_billing_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid billing type. Must be one of: {', '.join(valid_billing_types)}"
        )
    
    # Get next report number
    report_number = get_next_report_number(db)
    
    db_report = ServiceReport(
        report_number=report_number,
        date=report_data.date,
        created_by=current_user.id,
        client_id=report_data.client_id,
        requested_by_id=report_data.requested_by_id,
        equipment_id=report_data.equipment_id,
        technician_id=current_user.id,
        service_type=report_data.service_type,
        billing_type=report_data.billing_type,
        battery_percentage=report_data.battery_percentage,
        horometer_readings=report_data.horometer_readings,
        work_performed=report_data.work_performed,
        detected_damages=report_data.detected_damages,
        possible_causes=report_data.possible_causes,
        activities_performed=report_data.activities_performed,
        operation_points=report_data.operation_points,
        inspection_items=report_data.inspection_items,
        technician_comments=report_data.technician_comments,
        applied_parts=report_data.applied_parts,
        work_time=report_data.work_time,
        status="pending"
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    return db_report

@router.put("/{report_id}", response_model=ServiceReportResponse)
async def update_service_report(
    report_id: int,
    report_data: ServiceReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update service report."""
    report = db.query(ServiceReport).filter(ServiceReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service report not found"
        )
    
    # Role-based access control
    if current_user.role == "operador":
        # Operators can only edit their own pending reports
        if report.technician_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        if report.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit completed reports"
            )
    elif current_user.role == "jefe":
        # Supervisors can approve reports (change status to completed)
        if report_data.status and report_data.status not in ["pending", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be 'pending' or 'completed'"
            )
    
    # Validate service type if being updated
    if report_data.service_type:
        valid_service_types = ["Preventivo", "Correctivo", "Instalación", "Reparación", "Otro"]
        if report_data.service_type not in valid_service_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid service type. Must be one of: {', '.join(valid_service_types)}"
            )
    
    # Validate billing type if being updated
    if report_data.billing_type:
        valid_billing_types = ["Facturación", "Renta", "Garantía", "Sin costo"]
        if report_data.billing_type not in valid_billing_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid billing type. Must be one of: {', '.join(valid_billing_types)}"
            )
    
    update_data = report_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    return report

@router.delete("/{report_id}")
async def delete_service_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete service report."""
    report = db.query(ServiceReport).filter(ServiceReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service report not found"
        )
    
    # Role-based access control
    if current_user.role == "operador":
        # Operators can only delete their own pending reports
        if report.technician_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        if report.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete completed reports"
            )
    elif current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(report)
    db.commit()
    
    return {"message": "Service report deleted successfully"}

@router.post("/{report_id}/upload-signature")
async def upload_signature(
    report_id: int,
    signature_type: str,  # "client" or "technician"
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload signature for service report."""
    report = db.query(ServiceReport).filter(ServiceReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service report not found"
        )
    
    # Validate signature type
    if signature_type not in ["client", "technician"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature type. Must be 'client' or 'technician'"
        )
    
    # Validate file type
    if file.content_type not in settings.allowed_image_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG are allowed"
        )
    
    # Create filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'png'
    filename = f"{signature_type}_signature_{report_id}_{uuid.uuid4().hex}.{file_extension}"
    file_path = f"/uploads/signatures/{filename}"
    
    # Create directory if not exists
    os.makedirs("/uploads/signatures", exist_ok=True)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Update report
    if signature_type == "client":
        report.client_signature = f"/uploads/signatures/{filename}"
    else:
        report.technician_signature = f"/uploads/signatures/{filename}"
    
    db.commit()
    
    return {"message": "Signature uploaded successfully", "file_path": file_path}

@router.get("/statistics/dashboard")
async def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard statistics."""
    query = db.query(ServiceReport)
    
    # Role-based filtering
    if current_user.role == "operador":
        query = query.filter(ServiceReport.technician_id == current_user.id)
    
    total_reports = query.count()
    pending_reports = query.filter(ServiceReport.status == "pending").count()
    completed_reports = query.filter(ServiceReport.status == "completed").count()
    
    # Additional stats for admin/jefe
    stats = {
        "total_reports": total_reports,
        "pending_reports": pending_reports,
        "completed_reports": completed_reports
    }
    
    if current_user.role in ["admin", "jefe"]:
        # Get client count
        client_count = db.query(Client).count()
        
        # Get technician count
        technician_count = db.query(User).filter(User.role == "operador").count()
        
        # Get equipment count
        equipment_count = db.query(Equipment).count()
        
        stats.update({
            "client_count": client_count,
            "technician_count": technician_count,
            "equipment_count": equipment_count
        })
    
    return stats

@router.get("/{report_id}/pdf")
async def generate_report_pdf(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate PDF for service report."""
    report = db.query(ServiceReport).filter(ServiceReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service report not found"
        )
    
    # Role-based access control
    if current_user.role == "operador" and report.technician_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        # Prepare data for PDF
        pdf_data = {
            "report_number": report.report_number,
            "date": report.date,
            "client": {
                "name": report.client.name,
                "address": report.client.address
            },
            "requested_by": {
                "name": report.requested_by.name,
                "position": report.requested_by.position
            },
            "equipment": {
                "type": report.equipment.type,
                "brand": report.equipment.brand,
                "model": report.equipment.model,
                "serial_number": report.equipment.serial_number
            },
            "technician": {
                "name": report.technician.name,
                "position": report.technician.position
            },
            "service_type": report.service_type,
            "billing_type": report.billing_type,
            "battery_percentage": report.battery_percentage,
            "horometer_readings": report.horometer_readings,
            "work_performed": report.work_performed,
            "detected_damages": report.detected_damages,
            "possible_causes": report.possible_causes,
            "activities_performed": report.activities_performed,
            "operation_points": report.operation_points,
            "inspection_items": report.inspection_items,
            "technician_comments": report.technician_comments,
            "applied_parts": report.applied_parts,
            "work_time": report.work_time,
            "status": report.status
        }
        
        # Generate PDF
        pdf_buffer = generate_service_report_pdf(pdf_data)
        
        # Return PDF as response
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_{report.report_number}.pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {str(e)}"
        )

@router.get("/{report_id}/pdf")
async def generate_report_pdf(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate PDF for service report."""
    report = db.query(ServiceReport).filter(ServiceReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service report not found"
        )
    
    # Role-based access control
    if current_user.role == "operador" and report.technician_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Prepare data for PDF generation
    pdf_data = {
        "report_number": report.report_number,
        "date": report.date,
        "client": {
            "name": report.client.name,
            "address": report.client.address
        },
        "requested_by": {
            "name": report.requested_by.name,
            "position": report.requested_by.position
        },
        "equipment": {
            "type": report.equipment.type,
            "brand": report.equipment.brand,
            "model": report.equipment.model,
            "serial_number": report.equipment.serial_number
        },
        "service_type": report.service_type,
        "billing_type": report.billing_type,
        "battery_percentage": report.battery_percentage,
        "horometer_readings": report.horometer_readings,
        "work_performed": report.work_performed,
        "detected_damages": report.detected_damages,
        "possible_causes": report.possible_causes,
        "activities_performed": report.activities_performed,
        "operation_points": report.operation_points,
        "inspection_items": report.inspection_items,
        "technician_comments": report.technician_comments,
        "applied_parts": report.applied_parts,
        "work_time": report.work_time,
        "technician": {
            "name": report.technician.name,
            "position": report.technician.position
        },
        "status": report.status
    }
    
    # Generate PDF
    try:
        pdf_buffer = generate_service_report_pdf(pdf_data)
        
        # Return PDF as response
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_servicio_{report.report_number}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {str(e)}"
        )
