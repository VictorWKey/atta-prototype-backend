from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os
from datetime import datetime
from typing import Dict, Any

def generate_service_report_pdf(report_data: Dict[str, Any]) -> BytesIO:
    """
    Generate a professional PDF for service report.
    ReportLab provides complete control over PDF layout and styling.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.8*inch,
        bottomMargin=0.8*inch
    )
    
    # Story will hold all the elements
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#eb0627'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#eb0627'),
        fontName='Helvetica-Bold',
        spaceBefore=15,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica'
    )
    
    # Header with logo and company info
    header_data = [
        ['ATTA MONTACARGAS', f"REPORTE #{report_data.get('report_number', 'N/A')}"],
        ['EXPERTOS EN MONTACARGAS', f"Fecha: {report_data.get('date', 'N/A')}"],
        ['TEL: 33 31 46 11 76', ''],
        ['www.attamontacargas.com', '']
    ]
    
    header_table = Table(header_data, colWidths=[3*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 3), 12),
        ('FONTNAME', (1, 0), (1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 0), (1, 1), 11),
        ('TEXTCOLOR', (0, 0), (0, 3), colors.HexColor('#eb0627')),
        ('TEXTCOLOR', (1, 0), (1, 1), colors.HexColor('#eb0627')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    # Title
    story.append(Paragraph("REPORTE DE SERVICIO", title_style))
    story.append(Spacer(1, 15))
    
    # Client Information
    story.append(Paragraph("INFORMACIÓN DEL CLIENTE", heading_style))
    
    client_data = [
        ['Cliente:', report_data.get('client', {}).get('name', 'N/A')],
        ['Solicitado por:', report_data.get('requested_by', {}).get('name', 'N/A')],
        ['Dirección:', report_data.get('client', {}).get('address', 'N/A')]
    ]
    
    client_table = Table(client_data, colWidths=[1.5*inch, 4*inch])
    client_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
    ]))
    
    story.append(client_table)
    story.append(Spacer(1, 15))
    
    # Equipment Information
    story.append(Paragraph("INFORMACIÓN DEL EQUIPO", heading_style))
    
    equipment = report_data.get('equipment', {})
    equipment_data = [
        ['Tipo:', equipment.get('type', 'N/A')],
        ['Marca:', equipment.get('brand', 'N/A')],
        ['Modelo:', equipment.get('model', 'N/A')],
        ['No. Serie:', equipment.get('serial_number', 'N/A')],
        ['Tipo de Servicio:', report_data.get('service_type', 'N/A')],
        ['Tipo de Facturación:', report_data.get('billing_type', 'N/A')]
    ]
    
    equipment_table = Table(equipment_data, colWidths=[1.5*inch, 4*inch])
    equipment_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
    ]))
    
    story.append(equipment_table)
    story.append(Spacer(1, 15))
    
    # Readings
    story.append(Paragraph("LECTURAS Y MEDICIONES", heading_style))
    
    horometer_readings = report_data.get('horometer_readings', {})
    battery = report_data.get('battery_percentage', 'N/A')
    
    readings_data = [
        ['H1:', str(horometer_readings.get('h1', 'N/A'))],
        ['H2:', str(horometer_readings.get('h2', 'N/A'))],
        ['H3:', str(horometer_readings.get('h3', 'N/A'))],
        ['H4:', str(horometer_readings.get('h4', 'N/A'))],
        ['Batería:', f"{battery}%" if battery != 'N/A' else 'N/A']
    ]
    
    readings_table = Table(readings_data, colWidths=[1.5*inch, 4*inch])
    readings_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
    ]))
    
    story.append(readings_table)
    story.append(Spacer(1, 15))
    
    # Work Details
    story.append(Paragraph("DETALLES DEL TRABAJO", heading_style))
    
    work_data = [
        ['Trabajo Realizado:', report_data.get('work_performed', 'N/A')],
        ['Daños Detectados:', report_data.get('detected_damages', 'N/A')],
        ['Actividades Realizadas:', report_data.get('activities_performed', 'N/A')]
    ]
    
    work_table = Table(work_data, colWidths=[1.5*inch, 4*inch])
    work_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
    ]))
    
    story.append(work_table)
    story.append(Spacer(1, 15))
    
    # Inspection Items (if available)
    inspection_items = report_data.get('inspection_items', [])
    if inspection_items:
        story.append(Paragraph("INSPECCIÓN", heading_style))
        
        # Group by category
        categories = {}
        for item in inspection_items:
            category = item.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        for category, items in categories.items():
            story.append(Paragraph(f"{category}:", ParagraphStyle('CategoryTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10)))
            
            inspection_data = [['Item', 'Estado']]
            for item in items:
                status_text = item.get('status', 'N/A')
                if status_text == 'OK':
                    status_text = '✓ OK'
                elif status_text == 'R':
                    status_text = '⚠ Requiere Atención'
                elif status_text == 'NA':
                    status_text = '— N/A'
                
                inspection_data.append([item.get('name', 'N/A'), status_text])
            
            inspection_table = Table(inspection_data, colWidths=[3*inch, 2*inch])
            inspection_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ]))
            
            story.append(inspection_table)
            story.append(Spacer(1, 10))
    
    # Comments
    comments = report_data.get('technician_comments', '')
    if comments:
        story.append(Paragraph("COMENTARIOS DEL TÉCNICO", heading_style))
        story.append(Paragraph(comments, normal_style))
        story.append(Spacer(1, 15))
    
    # Work Time
    work_time = report_data.get('work_time', {})
    if work_time:
        story.append(Paragraph("TIEMPO DE TRABAJO", heading_style))
        
        time_data = [
            ['Fecha:', work_time.get('date', 'N/A')],
            ['Hora de Entrada:', work_time.get('entryTime', 'N/A')],
            ['Hora de Salida:', work_time.get('exitTime', 'N/A')],
            ['Total de Horas:', str(work_time.get('totalHours', 'N/A'))]
        ]
        
        time_table = Table(time_data, colWidths=[1.5*inch, 4*inch])
        time_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ]))
        
        story.append(time_table)
        story.append(Spacer(1, 20))
    
    # Signatures section
    story.append(Paragraph("FIRMAS", heading_style))
    
    signature_data = [
        ['TÉCNICO', 'CLIENTE'],
        ['', ''],
        ['', ''],
        [f"Nombre: {report_data.get('technician', {}).get('name', 'N/A')}", f"Nombre: {report_data.get('requested_by', {}).get('name', 'N/A')}"],
        [f"Fecha: {report_data.get('date', 'N/A')}", f"Fecha: {report_data.get('date', 'N/A')}"]
    ]
    
    signature_table = Table(signature_data, colWidths=[2.5*inch, 2.5*inch], rowHeights=[0.3*inch, 0.8*inch, 0.3*inch, 0.3*inch, 0.3*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 1), (-1, 2), 'MIDDLE'),
        ('VALIGN', (0, 3), (-1, -1), 'TOP'),
    ]))
    
    story.append(signature_table)
    
    # Footer
    story.append(Spacer(1, 30))
    footer_text = "Este reporte ha sido generado digitalmente por ATTA MONTACARGAS"
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer
