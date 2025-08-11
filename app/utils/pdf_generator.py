from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
    
    # === SECCIÓN 13: PIE DE PÁGINA ===ort inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os
from datetime import datetime
from typing import Dict, Any

# Configuración de colores corporativos ATTA MONTACARGAS
# Puedes modificar estos colores para personalizar el diseño
CORPORATE_COLORS = {
    'primary': '#eb0627',      # Rojo corporativo principal
    'secondary': '#2c3e50',    # Gris azulado para texto secundario
    'accent': '#34495e',       # Gris oscuro para acentos
    'light_gray': '#f5f5f5',   # Gris claro para fondos
    'medium_gray': '#ecf0f1',  # Gris medio para separadores
    'success': '#27ae60',      # Verde para estados OK
    'warning': '#f39c12',      # Naranja para advertencias
    'danger': '#e74c3c'        # Rojo para errores
}

# Configuración de fuentes
# Puedes cambiar las fuentes aquí para personalizar la tipografía
FONTS = {
    'title': 'Helvetica-Bold',
    'heading': 'Helvetica-Bold', 
    'normal': 'Helvetica',
    'italic': 'Helvetica-Oblique'
}

# Configuración de tamaños de fuente
FONT_SIZES = {
    'title': 18,
    'heading': 12,
    'subheading': 10,
    'normal': 10,
    'small': 8,
    'footer': 8
}

def generate_service_report_pdf(report_data: Dict[str, Any]) -> BytesIO:
    """
    Genera un PDF profesional para reporte de servicio usando ReportLab.
    
    Esta función crea un PDF completamente personalizable con control total
    sobre el diseño, colores, fuentes, e imágenes. El PDF se genera en memoria
    sin guardarse en disco.
    
    Args:
        report_data: Diccionario con todos los datos del reporte
        
    Returns:
        BytesIO: Buffer de memoria con el PDF generado
        
    Personalización:
    - Modifica CORPORATE_COLORS para cambiar la paleta de colores
    - Modifica FONTS para cambiar las tipografías
    - Modifica FONT_SIZES para ajustar tamaños de texto
    - Agrega secciones nuevas copiando el patrón de las existentes
    """
    # Crear buffer de memoria para el PDF
    buffer = BytesIO()
    
    # Configurar documento con márgenes personalizables
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.8*inch,
        bottomMargin=0.8*inch
    )
    
    # Lista que contendrá todos los elementos del PDF
    story = []
    
    # Obtener estilos base de ReportLab
    styles = getSampleStyleSheet()
    
    # Crear estilos personalizados
    # Puedes modificar estos estilos para cambiar la apariencia
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=FONT_SIZES['title'],
        textColor=colors.HexColor(CORPORATE_COLORS['primary']),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName=FONTS['title']
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=FONT_SIZES['heading'],
        textColor=colors.HexColor(CORPORATE_COLORS['primary']),
        fontName=FONTS['heading'],
        spaceBefore=15,
        spaceAfter=10
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Normal'],
        fontSize=FONT_SIZES['subheading'],
        textColor=colors.HexColor(CORPORATE_COLORS['secondary']),
        fontName=FONTS['heading'],
        spaceBefore=10,
        spaceAfter=5
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=FONT_SIZES['normal'],
        fontName=FONTS['normal']
    )
    
    # === SECCIÓN 1: ENCABEZADO CORPORATIVO ===
    # Puedes personalizar la información de la empresa aquí
    story.append(_create_header_section(report_data))
    story.append(Spacer(1, 20))
    
    # === SECCIÓN 2: TÍTULO PRINCIPAL ===
    story.append(Paragraph("REPORTE DE SERVICIO", title_style))
    story.append(Spacer(1, 15))
    
    # === SECCIÓN 3: INFORMACIÓN DEL CLIENTE ===
    story.extend(_create_client_section(report_data, heading_style))
    story.append(Spacer(1, 15))
    
    # === SECCIÓN 4: INFORMACIÓN DEL EQUIPO ===
    story.extend(_create_equipment_section(report_data, heading_style))
    story.append(Spacer(1, 15))
    
    # === SECCIÓN 5: LECTURAS Y MEDICIONES ===
    story.extend(_create_readings_section(report_data, heading_style))
    story.append(Spacer(1, 15))
    
    # === SECCIÓN 6: PUNTOS DE OPERACIÓN ===
    if report_data.get('operation_points'):
        story.extend(_create_operation_points_section(report_data, heading_style))
        story.append(Spacer(1, 15))
    
    # === SECCIÓN 7: DETALLES DEL TRABAJO ===
    story.extend(_create_work_details_section(report_data, heading_style))
    story.append(Spacer(1, 15))
    
    # === SECCIÓN 8: INSPECCIÓN (si hay items) ===
    if report_data.get('inspection_items'):
        story.extend(_create_inspection_section(report_data, heading_style, styles))
        story.append(Spacer(1, 15))
    
    # === SECCIÓN 9: COMENTARIOS DEL TÉCNICO ===
    if report_data.get('technician_comments'):
        story.extend(_create_comments_section(report_data, heading_style, normal_style))
        story.append(Spacer(1, 15))
    
    # === SECCIÓN 10: REFACCIONES Y CONSUMIBLES ===
    if report_data.get('applied_parts'):
        story.extend(_create_applied_parts_section(report_data, heading_style))
        story.append(Spacer(1, 15))
    
    # === SECCIÓN 11: TIEMPO DE TRABAJO ===
    if report_data.get('work_time'):
        story.extend(_create_work_time_section(report_data, heading_style))
        story.append(Spacer(1, 20))
    
    # === SECCIÓN 11: FIRMAS ===
    story.extend(_create_signatures_section(report_data, heading_style))
    
    # === SECCIÓN 12: PIE DE PÁGINA ===
    story.extend(_create_footer_section(styles))
    
    # Construir el PDF
    doc.build(story)
    
    # Regresar al inicio del buffer
    buffer.seek(0)
    return buffer


def _create_header_section(report_data: Dict[str, Any]) -> Table:
    """
    Crea la sección de encabezado con información corporativa.
    Personaliza aquí el logo y datos de la empresa.
    """
    header_data = [
        ['ATTA MONTACARGAS', f"REPORTE #{report_data.get('report_number', 'N/A')}"],
        ['EXPERTOS EN MONTACARGAS', f"Fecha: {report_data.get('date', 'N/A')}"],
        ['TEL: 33 31 46 11 76', ''],
        ['www.attamontacargas.com', '']
    ]
    
    header_table = Table(header_data, colWidths=[3*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, 3), FONTS['heading']),
        ('FONTSIZE', (0, 0), (0, 3), FONT_SIZES['heading']),
        ('FONTNAME', (1, 0), (1, 1), FONTS['heading']),
        ('FONTSIZE', (1, 0), (1, 1), FONT_SIZES['subheading']),
        ('TEXTCOLOR', (0, 0), (0, 3), colors.HexColor(CORPORATE_COLORS['primary'])),
        ('TEXTCOLOR', (1, 0), (1, 1), colors.HexColor(CORPORATE_COLORS['primary'])),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    return header_table


def _create_client_section(report_data: Dict[str, Any], heading_style: ParagraphStyle) -> list:
    """
    Crea la sección de información del cliente.
    """
    elements = []
    elements.append(Paragraph("INFORMACIÓN DEL CLIENTE", heading_style))
    
    client_data = [
        ['Cliente:', report_data.get('client', {}).get('name', 'N/A')],
        ['Solicitado por:', report_data.get('requested_by', {}).get('name', 'N/A')],
        ['Dirección:', report_data.get('client', {}).get('address', 'N/A')]
    ]
    
    client_table = Table(client_data, colWidths=[1.5*inch, 4*inch])
    client_table.setStyle(_get_standard_table_style())
    
    elements.append(client_table)
    return elements


def _create_equipment_section(report_data: Dict[str, Any], heading_style: ParagraphStyle) -> list:
    """
    Crea la sección de información del equipo.
    """
    elements = []
    elements.append(Paragraph("INFORMACIÓN DEL EQUIPO Y TÉCNICO", heading_style))
    
    equipment = report_data.get('equipment', {})
    technician = report_data.get('technician', {})
    specs = report_data.get('equipment_specifications', {})
    
    equipment_data = [
        ['Tipo de Equipo:', equipment.get('type', 'N/A')],
        ['Marca:', equipment.get('brand', 'N/A')],
        ['Modelo:', equipment.get('model', 'N/A')],
        ['No. Serie:', equipment.get('serial_number', 'N/A')],
        ['Año del Modelo:', specs.get('model_year', 'N/A')],
        ['Capacidad:', specs.get('capacity', 'N/A')],
        ['Tipo de Combustible:', specs.get('fuel_type', 'N/A')],
        ['Técnico de Servicio:', technician.get('name', 'N/A')],
        ['Posición:', technician.get('position', 'N/A')],
        ['Tipo de Servicio:', report_data.get('service_type', 'N/A')],
        ['Tipo de Facturación:', report_data.get('billing_type', 'N/A')],
        ['Porcentaje de Batería:', f"{report_data.get('battery_percentage', 'N/A')}%" if report_data.get('battery_percentage') else 'N/A']
    ]
    
    equipment_table = Table(equipment_data, colWidths=[2.2*inch, 3.8*inch])
    equipment_table.setStyle(_get_standard_table_style())
    
    elements.append(equipment_table)
    return elements


def _create_readings_section(report_data: Dict[str, Any], heading_style: ParagraphStyle) -> list:
    """
    Crea la sección de lecturas y mediciones.
    """
    elements = []
    elements.append(Paragraph("LECTURAS Y MEDICIONES", heading_style))
    
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
    readings_table.setStyle(_get_standard_table_style())
    
    elements.append(readings_table)
    return elements


def _create_operation_points_section(report_data: Dict[str, Any], heading_style: ParagraphStyle) -> list:
    """
    Crea la sección de puntos de operación.
    """
    elements = []
    elements.append(Paragraph("PUNTOS DE OPERACIÓN", heading_style))
    
    operation_points = report_data.get('operation_points', {})
    
    operation_data = [
        ['Velocidad de Avance:', f"{operation_points.get('velocidad_avance', 'N/A')} Km/h" if operation_points.get('velocidad_avance') else 'N/A'],
        ['Funciones Auxiliares Operando:', operation_points.get('funciones_auxiliares_operando', 'N/A')],
        ['Paro de Emergencia Dentro de Especificaciones:', operation_points.get('paro_emergencia_especificaciones', 'N/A')],
        ['Sistema:', operation_points.get('sistema', 'N/A')],
        ['Objeto de Inspección:', operation_points.get('objeto_inspeccion', 'N/A')]
    ]
    
    operation_table = Table(operation_data, colWidths=[3*inch, 3*inch])
    operation_table.setStyle(_get_standard_table_style())
    
    elements.append(operation_table)
    return elements


def _create_work_details_section(report_data: Dict[str, Any], heading_style: ParagraphStyle) -> list:
    """
    Crea la sección de detalles del trabajo.
    """
    elements = []
    elements.append(Paragraph("DETALLES DEL TRABAJO", heading_style))
    
    # Crear estilos para texto largo
    text_style = ParagraphStyle(
        'WorkText',
        fontName=FONTS['normal'],
        fontSize=9,
        leading=11,
        spaceAfter=6
    )
    
    # Usar Paragraph para permitir texto multilínea
    work_performed = Paragraph(report_data.get('work_performed', 'N/A'), text_style)
    detected_damages = Paragraph(report_data.get('detected_damages', 'N/A'), text_style)
    activities_performed = Paragraph(report_data.get('activities_performed', 'N/A'), text_style)
    
    work_data = [
        ['Trabajo Realizado:', work_performed],
        ['Daños Detectados:', detected_damages],
        ['Actividades Realizadas:', activities_performed]
    ]
    
    work_table = Table(work_data, colWidths=[1.5*inch, 4*inch])
    work_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), FONTS['heading']),
        ('FONTSIZE', (0, 0), (0, -1), 10),
        ('FONTSIZE', (1, 0), (1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(CORPORATE_COLORS['light_gray'])),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    elements.append(work_table)
    return elements


def _create_inspection_section(report_data: Dict[str, Any], heading_style: ParagraphStyle, styles) -> list:
    """
    Crea la sección de inspección agrupada por categorías.
    """
    elements = []
    elements.append(Paragraph("INSPECCIÓN", heading_style))
    
    inspection_items = report_data.get('inspection_items', [])
    
    # Los datos vienen como una lista de objetos con categoría e items
    for category_data in inspection_items:
        if isinstance(category_data, dict) and 'category' in category_data and 'items' in category_data:
            category = category_data['category']
            items = category_data['items']
            
            # Título de categoría
            category_style = ParagraphStyle(
                'CategoryTitle', 
                parent=styles['Normal'], 
                fontName=FONTS['heading'], 
                fontSize=FONT_SIZES['subheading']
            )
            elements.append(Paragraph(f"{category}:", category_style))
            
            # Tabla de items de inspección
            inspection_data = [['Item', 'Estado']]
            for item in items:
                item_name = item.get('name', 'N/A')
                status_text = _format_inspection_status(item.get('status', 'N/A'))
                
                # Usar Paragraph para permitir texto multilínea si es necesario
                item_para = Paragraph(item_name, ParagraphStyle('ItemText', parent=styles['Normal'], fontSize=9))
                status_para = Paragraph(status_text, ParagraphStyle('StatusText', parent=styles['Normal'], fontSize=9))
                
                inspection_data.append([item_para, status_para])
            
            inspection_table = Table(inspection_data, colWidths=[3.5*inch, 1.5*inch])
            inspection_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), FONTS['heading']),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(CORPORATE_COLORS['medium_gray'])),
            ]))
            
            elements.append(inspection_table)
            elements.append(Spacer(1, 10))
    
    return elements


def _create_comments_section(report_data: Dict[str, Any], heading_style: ParagraphStyle, normal_style: ParagraphStyle) -> list:
    """
    Crea la sección de comentarios del técnico.
    """
    elements = []
    elements.append(Paragraph("COMENTARIOS DEL TÉCNICO", heading_style))
    elements.append(Paragraph(report_data.get('technician_comments', ''), normal_style))
    return elements


def _create_applied_parts_section(report_data: Dict[str, Any], heading_style: ParagraphStyle) -> list:
    """
    Crea la sección de refacciones y consumibles aplicados.
    """
    elements = []
    elements.append(Paragraph("REFACCIONES Y CONSUMIBLES APLICADOS", heading_style))
    
    applied_parts = report_data.get('applied_parts', [])
    
    if applied_parts:
        # Separar por tipo
        refacciones = [part for part in applied_parts if part.get('type') == 'refacciones']
        consumibles = [part for part in applied_parts if part.get('type') == 'consumibles']
        
        parts_data = []
        parts_data.append(['TIPO', 'DESCRIPCIÓN', 'CANTIDAD'])
        
        # Agregar refacciones
        if refacciones:
            for part in refacciones:
                parts_data.append(['Refacciones', part.get('description', 'N/A'), part.get('quantity', 'N/A')])
        
        # Agregar consumibles
        if consumibles:
            for part in consumibles:
                parts_data.append(['Consumibles', part.get('description', 'N/A'), part.get('quantity', 'N/A')])
        
        parts_table = Table(parts_data, colWidths=[1.5*inch, 3*inch, 1.5*inch])
        parts_table.setStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8E8E8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        
        elements.append(parts_table)
    else:
        elements.append(Paragraph("No se aplicaron refacciones ni consumibles.", heading_style))
    
    return elements


def _create_work_time_section(report_data: Dict[str, Any], heading_style: ParagraphStyle) -> list:
    """
    Crea la sección de tiempo de trabajo.
    """
    elements = []
    elements.append(Paragraph("TIEMPO DE TRABAJO", heading_style))
    
    work_time = report_data.get('work_time', {})
    time_data = [
        ['Fecha:', work_time.get('fecha', 'N/A')],
        ['Hora de Entrada:', work_time.get('hora_entrada', 'N/A')],
        ['Hora de Salida:', work_time.get('hora_salida', 'N/A')],
        ['Total de Horas:', str(work_time.get('total_horas', 'N/A'))]
    ]
    
    time_table = Table(time_data, colWidths=[1.5*inch, 4*inch])
    time_table.setStyle(_get_standard_table_style())
    
    elements.append(time_table)
    return elements


def _create_signatures_section(report_data: Dict[str, Any], heading_style: ParagraphStyle) -> list:
    """
    Crea la sección de firmas.
    """
    elements = []
    elements.append(Paragraph("FIRMAS", heading_style))
    
    signature_data = [
        ['TÉCNICO', 'CLIENTE'],
        ['', ''],  # Espacio para firmas
        ['', ''],  # Espacio adicional
        [f"Nombre: {report_data.get('technician', {}).get('name', 'N/A')}", 
         f"Nombre: {report_data.get('requested_by', {}).get('name', 'N/A')}"],
        [f"Fecha: {report_data.get('date', 'N/A')}", 
         f"Fecha: {report_data.get('date', 'N/A')}"]
    ]
    
    signature_table = Table(
        signature_data, 
        colWidths=[2.5*inch, 2.5*inch], 
        rowHeights=[0.3*inch, 0.8*inch, 0.3*inch, 0.3*inch, 0.3*inch]
    )
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONTS['heading']),
        ('FONTSIZE', (0, 0), (-1, -1), FONT_SIZES['normal']),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 1), (-1, 2), 'MIDDLE'),
        ('VALIGN', (0, 3), (-1, -1), 'TOP'),
    ]))
    
    elements.append(signature_table)
    return elements


def _create_footer_section(styles) -> list:
    """
    Crea la sección de pie de página.
    """
    elements = []
    elements.append(Spacer(1, 30))
    
    footer_text = "Este reporte ha sido generado digitalmente por ATTA MONTACARGAS"
    footer_style = ParagraphStyle(
        'Footer', 
        parent=styles['Normal'], 
        fontSize=FONT_SIZES['footer'], 
        alignment=TA_CENTER, 
        textColor=colors.grey
    )
    elements.append(Paragraph(footer_text, footer_style))
    
    return elements


def _get_standard_table_style() -> TableStyle:
    """
    Retorna el estilo estándar para tablas.
    Puedes modificar este estilo para cambiar la apariencia de todas las tablas.
    """
    return TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), FONTS['heading']),
        ('FONTSIZE', (0, 0), (-1, -1), FONT_SIZES['normal']),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(CORPORATE_COLORS['light_gray'])),
    ])


def _format_inspection_status(status: str) -> str:
    """
    Formatea el estado de inspección con iconos visuales.
    Puedes personalizar los iconos y colores aquí.
    """
    status_map = {
        'OK': '✓ OK',
        'R': '⚠ Requiere Atención', 
        'NA': '— N/A',
        'N/A': '— N/A'
    }
    return status_map.get(status, status)
