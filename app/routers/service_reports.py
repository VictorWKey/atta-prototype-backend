from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import os
import uuid

from database import get_db
from models import User, ServiceReport, Client, Contact, Equipment
from schemas import (
    ServiceReportCreate, ServiceReportUpdate, ServiceReportResponse,
    OperationPoints, InspectionItem
)
from routers.auth import get_current_active_user
from core.config import settings
from utils.pdf_generator import generate_service_report_pdf
from fastapi.responses import Response

router = APIRouter()

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
    print(f"🔍 SERVICE REPORTS GET: User {current_user.name} (ID: {current_user.id}, Role: {current_user.role}) requesting reports")
    
    query = db.query(ServiceReport)
    
    # Role-based filtering
    if current_user.role == "operador":
        # Operators can only see reports they created
        print(f"🔒 FILTERING for operador: Only showing reports where created_by = {current_user.id}")
        query = query.filter(ServiceReport.created_by == current_user.id)
    else:
        print(f"🔓 NO FILTERING: User role '{current_user.role}' can see all reports")
    
    # Apply filters
    if status_filter:
        query = query.filter(ServiceReport.status == status_filter)
    
    if client_id:
        query = query.filter(ServiceReport.client_id == client_id)
    
    if technician_id and current_user.role in ["admin", "jefe"]:
        query = query.filter(ServiceReport.technician_id == technician_id)
    
    # Order by id descending (newest first)
    reports = query.order_by(desc(ServiceReport.id)).offset(skip).limit(limit).all()
    
    print(f"📊 QUERY RESULT: Found {len(reports)} reports for user {current_user.name}")
    if reports:
        for report in reports:
            print(f"  - Report #{report.id}: technician_id={report.technician_id}, created_by={report.created_by}")
    
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
    if current_user.role == "operador" and report.created_by != current_user.id:
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
    print(f"🔍 CREATE REPORT DEBUG - Status received: {getattr(report_data, 'status', 'NOT_SET')}")
    print(f"🔍 CREATE REPORT DEBUG - Pending reason: {getattr(report_data, 'pending_reason', 'NOT_SET')}")
    print(f"🔍 CREATE REPORT DEBUG - User: {current_user.name} (Role: {current_user.role})")
    
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
    
    # Convert Pydantic models to dict for JSON serialization
    equipment_specifications_dict = None
    if report_data.equipment_specifications:
        equipment_specifications_dict = report_data.equipment_specifications.model_dump()
    
    operation_points_dict = None
    if report_data.operation_points:
        operation_points_dict = report_data.operation_points.model_dump()
    
    inspection_items_dict = None
    if report_data.inspection_items:
        inspection_items_dict = [item.model_dump() for item in report_data.inspection_items]
    
    applied_parts_dict = None
    if report_data.applied_parts:
        applied_parts_dict = [part.model_dump() for part in report_data.applied_parts]
    
    work_time_dict = None
    if report_data.work_time:
        work_time_dict = report_data.work_time.model_dump()
    
    signatures_dict = None
    if report_data.signatures:
        signatures_dict = report_data.signatures.model_dump()

    # Determine pending reason
    pending_reason = report_data.pending_reason or "Reporte creado - pendiente de finalización"

    db_report = ServiceReport(
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
        equipment_specifications=equipment_specifications_dict,
        work_performed=report_data.work_performed,
        detected_damages=report_data.detected_damages,
        possible_causes=report_data.possible_causes,
        activities_performed=report_data.activities_performed,
        operation_points=operation_points_dict,
        inspection_items=inspection_items_dict,
        technician_comments=report_data.technician_comments,
        client_observations=report_data.client_observations,
        applied_parts=applied_parts_dict,
        work_time=work_time_dict,
        signatures=signatures_dict,
        status=report_data.status,
        pending_reason=pending_reason
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
    # Debug logging
    print(f"🔍 DEBUG: Updating report {report_id}")
    print(f"🔍 DEBUG: Request data type: {type(report_data)}")
    print(f"🔍 DEBUG: Request data: {report_data}")
    
    report = db.query(ServiceReport).filter(ServiceReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service report not found"
        )
    
    # Role-based access control
    if current_user.role == "operador":
        # Operators can only edit reports they created
        if report.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        if report.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit completed reports"
            )
        
        # If operator is setting status to pending, require a reason
        if report_data.status == "pending" and not report_data.pending_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="pending_reason is required when setting status to 'pending'"
            )
    elif current_user.role == "jefe":
        # Supervisors can approve reports (change status to completed)
        if report_data.status and report_data.status not in ["pending", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be 'pending' or 'completed'"
            )
        
        # Prevent changing completed reports back to pending
        if report.status == "completed" and report_data.status == "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change completed reports back to pending status"
            )
        
        # If setting status to pending, require a reason
        if report_data.status == "pending" and not report_data.pending_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="pending_reason is required when setting status to 'pending'"
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
    
    # Handle status transitions
    if "status" in update_data:
        if update_data["status"] == "completed":
            # Clear pending reason when completing a report
            update_data["pending_reason"] = None
        elif update_data["status"] == "pending" and not update_data.get("pending_reason"):
            # Ensure there's a pending reason when setting to pending
            if not report.pending_reason:  # Only if there wasn't already a reason
                update_data["pending_reason"] = "Reporte marcado como pendiente"
    
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
        # Operators can only delete reports they created
        if report.created_by != current_user.id:
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
        query = query.filter(ServiceReport.created_by == current_user.id)
    
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
    """
    Generate and download PDF for service report.
    
    Este endpoint genera un PDF del reporte de servicio usando ReportLab.
    El PDF se genera al momento sin guardarse en disco y se envía como respuesta
    para descarga directa.
    
    Args:
        report_id: ID del reporte de servicio
        db: Sesión de base de datos
        current_user: Usuario autenticado
    
    Returns:
        PDF file as application/pdf response
    
    Raises:
        404: Si el reporte no existe
        403: Si el usuario no tiene permisos para ver el reporte
        500: Si hay error generando el PDF
    """
    # Buscar el reporte en la base de datos
    report = db.query(ServiceReport).filter(ServiceReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service report not found"
        )
    
    # Control de acceso basado en roles
    # Los operadores solo pueden ver reportes que crearon
    if current_user.role == "operador" and report.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        # Preparar datos para la generación del PDF
        # Se estructuran todos los datos del reporte para el generador de PDF
        pdf_data = {
            "report_number": report.id,
            "date": report.date if report.date else "N/A",
            "client": {
                "name": report.client.name if report.client else "N/A",
                "address": report.client.address if report.client else "N/A"
            },
            "requested_by": {
                "name": report.requested_by.name if report.requested_by else "N/A",
                "position": report.requested_by.position if report.requested_by else "N/A"
            },
            "equipment": {
                "type": report.equipment.type if report.equipment else "N/A",
                "brand": report.equipment.brand if report.equipment else "N/A",
                "model": report.equipment.model if report.equipment else "N/A",
                "serial_number": report.equipment.serial_number if report.equipment else "N/A"
            },
            "technician": {
                "name": report.technician.name if report.technician else "N/A",
                "position": report.technician.position if report.technician else "N/A"
            },
            "service_type": report.service_type or "N/A",
            "billing_type": report.billing_type or "N/A",
            "battery_percentage": report.battery_percentage,
            "horometer_readings": report.horometer_readings or {},
            "work_performed": report.work_performed or "N/A",
            "detected_damages": report.detected_damages or "N/A",
            "possible_causes": report.possible_causes or "N/A",
            "activities_performed": report.activities_performed or "N/A",
            "operation_points": report.operation_points or "N/A",
            "inspection_items": report.inspection_items or [],
            "technician_comments": report.technician_comments or "",
            "applied_parts": report.applied_parts or [],
            "work_time": report.work_time or {},
            "status": report.status or "N/A"
        }
        
        # Generar PDF usando ReportLab - Versión Compacta
        # El generador devuelve un BytesIO buffer con el PDF
        from utils.pdf_generator_compact import generate_service_report_pdf_compact
        pdf_buffer = generate_service_report_pdf_compact(pdf_data)
        
        # Crear nombre de archivo descriptivo
        date_str = report.date.replace("-", "") if report.date else "sin_fecha"
        filename = f"reporte_servicio_{report.id}_{date_str}.pdf"
        
        # Retornar PDF como respuesta para descarga
        # Content-Disposition con attachment fuerza la descarga
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_buffer.getvalue())),
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except Exception as e:
        # Log del error para debugging
        print(f"Error generating PDF for report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {str(e)}"
        )

@router.get("/inspection-items/defaults")
async def get_default_inspection_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get default inspection items template from database"""
    # This endpoint is now deprecated - use /api/inspection/templates/service-report instead
    return {
        "message": "This endpoint is deprecated. Use /api/inspection/templates/service-report for updated templates from database.",
        "redirect_to": "/api/inspection/templates/service-report"
    }
