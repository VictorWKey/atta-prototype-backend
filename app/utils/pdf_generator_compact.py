from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
from typing import Dict, Any
import os


def generate_service_report_pdf_compact(report_data: Dict[str, Any]) -> BytesIO:
    """
    Genera un PDF compacto del reporte de servicio que cabe en una sola página.
    Diseño inspirado en el formato original con layout optimizado.
    """
    buffer = BytesIO()
    
    # Configurar documento para una página compacta con márgenes mínimos
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.15*inch,  # Reducido de 0.25 a 0.15
        leftMargin=0.15*inch,   # Reducido de 0.25 a 0.15
        topMargin=0.1*inch,     # Reducido de 0.2 a 0.1
        bottomMargin=0.1*inch   # Reducido de 0.2 a 0.1
    )
    
    story = []
    
    # === CREAR ESTILOS COMPACTOS ===
    section_style = ParagraphStyle(
        'CompactSection',
        fontSize=8,         # Reducido de 9 a 8
        textColor=colors.white,
        fontName='Helvetica-Bold',
        spaceBefore=2,
        spaceAfter=2,
        alignment=TA_CENTER,
        leading=9           # Reducido de 10 a 9
    )
    
    normal_style = ParagraphStyle(
        'CompactNormal',
        fontSize=6,         # Reducido de 7 a 6
        fontName='Helvetica',
        leading=7           # Reducido de 8 a 7
    )
    
    # === HEADER CORPORATIVO ===
    story.append(_create_compact_header(report_data))
    story.append(Spacer(1, 1))  # Reducido de 4 a 2
    
    # === INFORMACIÓN PRINCIPAL EN 2 COLUMNAS ===
    story.extend(_create_main_info_section(report_data, normal_style))
    story.append(Spacer(1, 8))  # Aumentado de 1 a 8 para más separación
    
    # === SECCIÓN DE TRABAJO REALIZADO EN DOS COLUMNAS ===
    story.extend(_create_work_section(report_data, section_style, normal_style))
    story.append(Spacer(1, 4))  # Aumentado de 1 a 4 para separación antes de comentarios
    
    # === SECCIÓN INFERIOR: PARTES, TIEMPO Y FIRMAS ===
    story.extend(_create_bottom_section(report_data, section_style, normal_style))
    
    # Construir el PDF
    doc.build(story)
    
    # Regresar al inicio del buffer
    buffer.seek(0)
    return buffer


def _create_compact_header(report_data: Dict[str, Any]) -> Table:
    """
    Crea el encabezado corporativo compacto estilo ATTA.
    """
    # Ruta del logo
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logo-atta-pdf.png")
    
    # Crear objeto de imagen con un tamaño adecuado
    logo_image = Image(logo_path, width=1.7*inch, height=0.7*inch)
    
    # Crear párrafo para información de teléfono y centrarla
    tel_paragraph = Paragraph('TELÉFONO<br/>33 31 46 11 76<br/>www.attamontacargas.com', 
                             ParagraphStyle('contact', fontSize=8, fontName='Helvetica', alignment=TA_CENTER))
    
    # Centrar todo el encabezado y juntar los elementos
    header_data = [
        [
            # Columna de logo e información de contacto (izquierda)
            Table([
                [logo_image],
                [tel_paragraph]
            ], colWidths=[2.5*inch], spaceBefore=0, spaceAfter=0),
            
            # Columna vacía central
            '',
            
            # Columna de reporte y fecha (derecha)
            Table([
                [Paragraph(f'<b>REPORTE DE SERVICIO</b><br/>#{report_data.get("report_number", "N/A")}', 
                         ParagraphStyle('header', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER))],
                [_create_date_box(report_data.get('date', 'N/A'))]
            ], colWidths=[2.5*inch], spaceBefore=0, spaceAfter=0)
        ]
    ]
    
    # Crear tabla principal con menos espacio entre columnas
    header_table = Table(header_data, colWidths=[3.3*inch, 0.15*inch, 3.35*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Centrado de columna izquierda
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),  # Centrado de columna derecha
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (2, 0), (2, 0), 0, colors.white),  # Sin bordes en el encabezado
    ]))
    
    return header_table


def _create_date_box(date_str: str) -> Table:
    """
    Crea la caja de fecha estilo formulario.
    """
    # Procesar fecha
    if date_str and date_str != 'N/A':
        parts = date_str.split('-')
        if len(parts) == 3:
            day, month, year = parts[2], parts[1], parts[0][2:]  # Formato: DD/MM/YY
        else:
            day, month, year = 'DD', 'MM', 'YY'
    else:
        day, month, year = 'DD', 'MM', 'YY'
    
    date_data = [
        ['DÍA', 'MES', 'AÑO'],
        [day, month, year]
    ]
    
    date_table = Table(date_data, colWidths=[0.8*inch, 0.8*inch, 0.9*inch])
    date_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    return date_table


def _create_main_info_section(report_data: Dict[str, Any], normal_style: ParagraphStyle) -> list:
    """
    Crea la sección principal de información en formato compacto.
    """
    elements = []
    
    # Información del cliente
    client_data = [
        ['Cliente:', '', 'Solicitado por:'],
        [report_data.get('client', {}).get('name', 'N/A'), '', 
         report_data.get('requested_by', {}).get('name', 'N/A')]
    ]
    
    client_table = Table(client_data, colWidths=[3.5*inch, 0.2*inch, 3.8*inch])  # Aumentado el ancho total
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.red),
        ('BACKGROUND', (2, 0), (2, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('TEXTCOLOR', (2, 0), (2, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),  # Reducido de 8 a 6
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (0, -1), 1, colors.black),
        ('GRID', (2, 0), (2, -1), 1, colors.black),
    ]))
    
    elements.append(client_table)
    
    # Dirección
    address_data = [
        ['Domicilio:', report_data.get('client', {}).get('address', 'N/A')]
    ]
    
    address_table = Table(address_data, colWidths=[1.2*inch, 6.3*inch])  # Aumentado el ancho total
    address_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(address_table)
    
    # Información del equipo
    equipment = report_data.get('equipment', {})
    specs = report_data.get('equipment_specifications', {})
    
    equipment_data = [
        ['Tipo de Equipo:', equipment.get('type', 'N/A'), 'Marca:', equipment.get('brand', 'N/A'), 
         'Modelo:', equipment.get('model', 'N/A'), 'Serie:', equipment.get('serial_number', 'N/A')]
    ]
    
    equipment_table = Table(equipment_data, colWidths=[1*inch, 1.1*inch, 0.6*inch, 0.9*inch, 0.6*inch, 0.9*inch, 0.6*inch, 1.4*inch])  # Ajustado para más ancho
    equipment_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(equipment_table)
    
    return elements


def _create_operation_points_table(report_data: Dict[str, Any], section_style: ParagraphStyle, normal_style: ParagraphStyle) -> list:
    """
    Crea una tabla separada para los puntos de operación.
    """
    elements = []
    
    operation_points = report_data.get('operation_points', {})
    
    # Crear tabla de puntos de operación
    op_data = [
        [Paragraph('SISTEMA', section_style), Paragraph('OBJETO DE INSPECCIÓN', section_style), 
         Paragraph('VELOCIDAD DE AVANCE', section_style)],
        [operation_points.get('sistema', 'N/A'), operation_points.get('objeto_inspeccion', 'N/A'), 
         f"{operation_points.get('velocidad_avance', 'N/A')} Km/h"]
    ]
    
    op_table = Table(op_data, colWidths=[2.5*inch, 3*inch, 2.5*inch])
    op_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Líneas más delgadas
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),    # Padding reducido
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1), # Padding reducido
        ('LEFTPADDING', (0, 0), (-1, -1), 2),   # Padding reducido
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),  # Padding reducido
    ]))
    
    elements.append(op_table)
    
    # Tabla adicional para funciones auxiliares
    aux_data = [
        ['FUNCIONES AUXILIARES OPERANDO', 'PARO EMERGENCIA ESPECIFICACIONES'],
        [operation_points.get('funciones_auxiliares_operando', 'N/A'), 
         operation_points.get('paro_emergencia_especificaciones', 'N/A')]
    ]
    
    aux_table = Table(aux_data, colWidths=[4*inch, 4*inch])
    aux_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Líneas más delgadas
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),    # Padding reducido
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1), # Padding reducido
        ('LEFTPADDING', (0, 0), (-1, -1), 2),   # Padding reducido
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),  # Padding reducido
    ]))
    
    elements.append(aux_table)
    
    return elements


def _create_separate_inspection(report_data: Dict[str, Any], section_style: ParagraphStyle) -> list:
    """
    Crea la tabla de inspección separada y compacta con 5 columnas.
    """
    elements = []
    
    # Preparar datos de inspección
    inspection_items = report_data.get('inspection_items', [])
    
    # Crear tabla de inspección con 5 columnas
    inspection_data = []
    
    # Headers principales de la tabla
    inspection_data.append([
        Paragraph('<b>SISTEMA</b>', ParagraphStyle('header', fontSize=5, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)),
        Paragraph('<b>OBJETO DE INSPECCIÓN</b>', ParagraphStyle('header', fontSize=5, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)),
        Paragraph('<b>OK</b>', ParagraphStyle('header', fontSize=5, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)),
        Paragraph('<b>N/A</b>', ParagraphStyle('header', fontSize=5, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)),
        Paragraph('<b>R</b>', ParagraphStyle('header', fontSize=5, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER))
    ])
    
    # Procesar todas las categorías y sus elementos
    for category_data in inspection_items:
        category_name = category_data.get('category', 'N/A')
        items = category_data.get('items', [])
        
        # Agregar items de la categoría
        for i, item in enumerate(items):
            status = item.get('status', 'N/A')
            item_name = item.get('name', 'N/A')
            
            # Determinar qué checkbox marcar según el status
            # Solo mostrar X cuando está marcado, vacío cuando no
            checkbox_ok = 'X' if status == 'OK' else ''
            checkbox_na = 'X' if status == 'N/A' else ''
            checkbox_r = 'X' if status == 'R' else ''
            
            # Solo mostrar el nombre del sistema en la primera fila de cada categoría
            sistema_text = category_name if i == 0 else ''
            
            item_row = [
                Paragraph(sistema_text, ParagraphStyle('sistema', fontSize=4, fontName='Helvetica-Bold' if i == 0 else 'Helvetica', alignment=TA_CENTER)),
                Paragraph(item_name, ParagraphStyle('item', fontSize=4, fontName='Helvetica')),
                Paragraph(checkbox_ok, ParagraphStyle('check', fontSize=6, alignment=TA_CENTER)),
                Paragraph(checkbox_na, ParagraphStyle('check', fontSize=6, alignment=TA_CENTER)), 
                Paragraph(checkbox_r, ParagraphStyle('check', fontSize=6, alignment=TA_CENTER))
            ]
            inspection_data.append(item_row)
    
    # Crear la tabla con anchos optimizados según el contenido
    # Crear tabla con altura reducida en las filas
    # Definir alturas específicas para cada fila (header y filas de contenido)
    inspection_table = Table(inspection_data, colWidths=[0.6*inch, 1.5*inch, 0.2*inch, 0.2*inch, 0.2*inch])

    
    inspection_table.setStyle(TableStyle([
        # Header principal con fondo rojo
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 5),  # Fuente más pequeña para headers
        
        # Configuración general
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),   # Columna SISTEMA centrada
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),     # OBJETO DE INSPECCIÓN alineado a la izquierda
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),  # Checkboxes centrados
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),     # Padding eliminado para reducir altura
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Padding eliminado para reducir altura
        ('LEFTPADDING', (0, 0), (-1, -1), 1),    # Padding horizontal mínimo
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),   # Padding horizontal mínimo
        ('FONTSIZE', (0, 1), (-1, -1), 4),       # Fuente muy pequeña para contenido
    ]))
    
    # Aplicar spans para agrupar visualmente cada sistema
    current_row = 1
    for category_data in inspection_items:
        items_count = len(category_data.get('items', []))
        if items_count > 1:
            # Hacer span vertical para el nombre del sistema cuando hay múltiples items
            inspection_table.setStyle(TableStyle([
                ('SPAN', (0, current_row), (0, current_row + items_count - 1)),
                ('VALIGN', (0, current_row), (0, current_row + items_count - 1), 'MIDDLE'),
            ]))
        current_row += items_count
    
    elements.append(inspection_table)
    
    return elements


def _create_work_section(report_data: Dict[str, Any], section_style: ParagraphStyle, normal_style: ParagraphStyle) -> list:
    """
    Crea las secciones de trabajo divididas en dos columnas: trabajo en la izquierda, inspección en la derecha.
    """
    elements = []
    
    # COLUMNA IZQUIERDA: Secciones de trabajo
    left_column_elements = []
    
    # Trabajo realizado
    work_content = report_data.get('work_performed', 'N/A')
    # Agregar espacio predeterminado
    work_content += '<br/><br/><br/><br/><br/><br/>'
    
    work_data = [
        [Paragraph('TRABAJO REALIZADO', section_style)],
        [Paragraph(work_content, normal_style)]
    ]
    
    work_table = Table(work_data, colWidths=[3.3*inch])
    work_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    left_column_elements.append(work_table)
    
    # Daños detectados
    damage_content = report_data.get('detected_damages', 'N/A')
    # Agregar espacio predeterminado
    damage_content += '<br/><br/><br/><br/><br/><br/>'
    
    damage_data = [
        [Paragraph('DAÑOS DETECTADOS', section_style)],
        [Paragraph(damage_content, normal_style)]
    ]
    
    damage_table = Table(damage_data, colWidths=[3.3*inch])
    damage_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    left_column_elements.append(damage_table)
    
    # Posibles causas
    causes_content = _format_possible_causes(report_data.get('possible_causes', []))
    # Agregar espacio predeterminado
    causes_content += '<br/><br/><br/><br/><br/><br/>'
    
    causes_data = [
        [Paragraph('POSIBLES CAUSAS', section_style)],
        [Paragraph(causes_content, normal_style)]
    ]
    
    causes_table = Table(causes_data, colWidths=[3.3*inch])
    causes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    left_column_elements.append(causes_table)
    
    # Actividades realizadas
    activities_content = report_data.get('activities_performed', 'N/A')
    # Agregar espacio predeterminado
    activities_content += '<br/><br/><br/><br/><br/><br/>'
    
    activities_data = [
        [Paragraph('ACTIVIDADES REALIZADAS', section_style)],
        [Paragraph(activities_content, normal_style)]
    ]
    
    activities_table = Table(activities_data, colWidths=[3.3*inch])
    activities_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    left_column_elements.append(activities_table)
    
    # Puntos de operación en la columna izquierda
    op_points = report_data.get('operation_points', {})
    
    # Crear subtabla con dos columnas para puntos de operación
    operation_subtable_data = [
        ['VELOCIDAD DE AVANCE', f'{op_points.get("velocidad_avance", "N/A")} Km/h'],
        ['FUNCIONES AUXILIARES OPERANDO', op_points.get("funciones_auxiliares_operando", "N/A")],
        ['PARO EMERGENCIA DENTRO DE ESPECIFICACIONES', op_points.get("paro_emergencia_especificaciones", "N/A")]
    ]
    
    operation_subtable = Table(operation_subtable_data, colWidths=[2.0*inch, 1.3*inch])
    operation_subtable.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Columna izquierda alineada a la izquierda
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),  # Columna derecha centrada
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),  # Valores en negrita
        # Sin bordes internos para evitar doble borde
    ]))
    
    # Tabla principal que contiene el título y la subtabla
    operation_data = [
        [Paragraph('PUNTOS DE OPERACIÓN', section_style)],
        [operation_subtable]
    ]
    
    operation_table = Table(operation_data, colWidths=[3.3*inch])
    operation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Solo la tabla externa tiene bordes
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    left_column_elements.append(operation_table)
    
    # COLUMNA DERECHA: Tabla de inspección
    right_column_elements = _create_separate_inspection(report_data, section_style)
    
    # Crear tabla de dos columnas
    main_content_data = [
        [left_column_elements, right_column_elements]
    ]
    
    main_content_table = Table(main_content_data, colWidths=[3.5*inch, 3.8*inch])
    main_content_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),    # Centrar la tabla completa
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (0, -1), 0),      # Sin padding izquierdo en columna izquierda
        ('RIGHTPADDING', (0, 0), (0, -1), 12),    # Más separación entre columnas
        ('LEFTPADDING', (1, 0), (1, -1), 12),     # Más separación entre columnas
        ('RIGHTPADDING', (1, 0), (1, -1), 0),     # Sin padding derecho en columna derecha
    ]))
    
    elements.append(main_content_table)
    
    return elements


def _create_compact_inspection(report_data: Dict[str, Any], section_style: ParagraphStyle) -> list:
    """
    Crea la sección de inspección compacta con checkboxes.
    """
    elements = []
    
    # Header de inspección
    inspection_header = [
        [Paragraph('INSPECCIÓN', section_style), '', 
         Paragraph('PUNTOS DE OPERACIÓN', section_style)]
    ]
    
    # Preparar datos de inspección
    inspection_items = report_data.get('inspection_items', [])
    inspection_categories = {}
    
    for category_data in inspection_items:
        category_name = category_data.get('category', 'N/A')
        items = category_data.get('items', [])
        inspection_categories[category_name] = items
    
    # Crear tabla de inspección con puntos de operación
    inspection_data = []
    inspection_data.append(['SISTEMA', 'OBJETO DE INSPECCIÓN'])
    
    # Agregar categorías de inspección
    for category, items in inspection_categories.items():
        if items:
            # Agregar header de categoría
            category_row = [Paragraph(f'<b>{category}</b>', 
                                    ParagraphStyle('cat', fontSize=7, fontName='Helvetica-Bold', textColor=colors.white)), '']
            inspection_data.append(category_row)
            
            # Agregar items de la categoría
            for item in items[:6]:  # Limitar items por espacio
                status = item.get('status', 'N/A')
                checkbox = '☑' if status == 'OK' else '☐' if status == 'R' else '—'
                item_name = item.get('name', 'N/A')
                inspection_data.append([item_name, checkbox])
    
    # Agregar puntos de operación en la columna derecha
    operation_points = report_data.get('operation_points', {})
    op_data = [
        f"VELOCIDAD DE AVANCE: {operation_points.get('velocidad_avance', 'N/A')} Km/h",
        f"FUNCIONES AUXILIARES OPERANDO: {operation_points.get('funciones_auxiliares_operando', 'N/A')}",
        f"PARO DE EMERGENCIA DENTRO DE ESPECIFICACIONES: {operation_points.get('paro_emergencia_especificaciones', 'N/A')}"
    ]
    
    # Combinar inspección y puntos de operación
    combined_data = []
    max_rows = max(len(inspection_data), len(op_data) + 2)
    
    for i in range(max_rows):
        left_col = inspection_data[i] if i < len(inspection_data) else ['', '']
        right_col = ''
        
        if i == 0:
            right_col = Paragraph('VELOCIDAD DE AVANCE', 
                                 ParagraphStyle('op', fontSize=7, fontName='Helvetica-Bold'))
        elif i == 1 and len(op_data) > 0:
            right_col = Paragraph(f"{operation_points.get('velocidad_avance', 'N/A')} Km/h", 
                                 ParagraphStyle('op', fontSize=7))
        elif i == 2:
            right_col = Paragraph('FUNCIONES AUXILIARES OPERANDO', 
                                 ParagraphStyle('op', fontSize=7, fontName='Helvetica-Bold'))
        elif i == 3:
            right_col = Paragraph(operation_points.get('funciones_auxiliares_operando', 'N/A'), 
                                 ParagraphStyle('op', fontSize=7))
        elif i == 4:
            right_col = Paragraph('PARO EMERGENCIA ESPECIFICACIONES', 
                                 ParagraphStyle('op', fontSize=7, fontName='Helvetica-Bold'))
        elif i == 5:
            right_col = Paragraph(operation_points.get('paro_emergencia_especificaciones', 'N/A'), 
                                 ParagraphStyle('op', fontSize=7))
        
        combined_data.append([left_col[0] if len(left_col) > 0 else '', 
                             left_col[1] if len(left_col) > 1 else '', 
                             right_col])
    
    inspection_table = Table(combined_data, colWidths=[3.5*inch, 0.5*inch, 3.5*inch])  # Aumentado el ancho total
    inspection_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.red),
        ('BACKGROUND', (2, 0), (2, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('TEXTCOLOR', (2, 0), (2, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
        ('GRID', (2, 0), (2, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(inspection_table)
    
    return elements


def _create_bottom_section(report_data: Dict[str, Any], section_style: ParagraphStyle, normal_style: ParagraphStyle) -> list:
    """
    Crea la sección inferior con partes, tiempo y firmas.
    """
    elements = []
    
    # Comentarios del técnico
    if report_data.get('technician_comments'):
        comments_data = [
            [Paragraph('COMENTARIOS DEL TÉCNICO', section_style)],
            [Paragraph(report_data.get('technician_comments', ''), normal_style)]
        ]
        
        comments_table = Table(comments_data, colWidths=[7.5*inch])  # Aumentado de 6.5 a 7.5
        comments_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(comments_table)
    
    # Refacciones y consumibles + Tiempo de trabajo
    parts_time_data = []
    
    # Header
    parts_time_data.append([
        Paragraph('REFACCIONES Y CONSUMIBLES APLICADOS', section_style),
        Paragraph('TIEMPO DE MANO DE OBRA', section_style)
    ])
    
    # Crear subtablas para cada sección
    applied_parts = report_data.get('applied_parts', [])
    
    # Subtabla de refacciones (dos columnas: descripción y cantidad)
    if applied_parts:
        parts_subtable_data = []
        for part in applied_parts:
            desc = part.get('description', 'N/A')
            qty = part.get('quantity', 'N/A')
            parts_subtable_data.append([desc, str(qty)])
    else:
        parts_subtable_data = [['No se aplicaron refacciones ni consumibles', '']]
    
    parts_subtable = Table(parts_subtable_data, colWidths=[2.8*inch, 0.95*inch])
    parts_subtable.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),     # Columna de descripción alineada a la izquierda
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),   # Columna de cantidad centrada
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),    # Reducido de 2 a 1
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1), # Reducido de 2 a 1
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),  # Cantidad en negrita
    ]))
    
    # Subtabla de tiempo (dos columnas: concepto y valor)
    work_time = report_data.get('work_time', {})
    time_subtable_data = [
        ['Fecha', work_time.get('fecha', 'N/A')],
        ['Hora Entrada', work_time.get('hora_entrada', 'N/A')],
        ['Hora Salida', work_time.get('hora_salida', 'N/A')],
        ['Total Horas', work_time.get('total_horas', 'N/A')]
    ]
    
    time_subtable = Table(time_subtable_data, colWidths=[1.8*inch, 1.95*inch])
    time_subtable.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),     # Columna de concepto alineada a la izquierda
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),   # Columna de valor centrada
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),    # Reducido de 2 a 1
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1), # Reducido de 2 a 1
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),  # Valores en negrita
    ]))
    
    # Contenido con las subtablas
    parts_time_data.append([
        parts_subtable,
        time_subtable
    ])
    
    parts_time_table = Table(parts_time_data, colWidths=[3.75*inch, 3.75*inch])  # Aumentado de 3.25 a 3.75
    parts_time_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(parts_time_table)
    
    # Firmas con información del creador del reporte
    signatures = report_data.get('signatures', {})
    created_by = report_data.get('created_by', {})
    creator_name = created_by.get('name', 'N/A')
    technician_name = signatures.get('technician', {}).get('name', 'TÉCNICO')
    client_name = signatures.get('client', {}).get('name', 'CLIENTE')
    
    # Crear texto combinado para el técnico con el creador del reporte
    tech_text = f"Técnico de servicio que valoró la inspección:\n{technician_name}"
    if creator_name != 'N/A' and creator_name != technician_name:
        tech_text = f"Técnico de servicio que valoró la inspección:\n{creator_name}"
    
    sig_data = [
        ['SELLO DE LA EMPRESA', 'CONFORMIDAD AUTORIZADA'],
        [
            Paragraph(tech_text, ParagraphStyle('tech_sig', fontSize=7, fontName='Helvetica', alignment=TA_CENTER, leading=8)),
            Paragraph(client_name, ParagraphStyle('client_sig', fontSize=7, fontName='Helvetica', alignment=TA_CENTER, leading=8))
        ]
    ]
    
    sig_table = Table(sig_data, colWidths=[3.75*inch, 3.75*inch], rowHeights=[0.25*inch, 0.6*inch])  # Reducido de 0.3 a 0.25
    sig_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 6),  # Reducido de 8 a 6
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    
    elements.append(sig_table)
    
    return elements


def _format_possible_causes(causes) -> str:
    """Formatea las posibles causas - solo muestra la causa seleccionada."""
    if not causes:
        return 'N/A'
    
    # Buscar solo la causa seleccionada
    for cause in causes:
        if isinstance(cause, dict):
            selected = cause.get('selected', False)
            if selected:
                return cause.get('name', 'N/A')
        else:
            # Si no es un dict, asumir que es la causa seleccionada
            return str(cause)
    
    # Si no hay ninguna seleccionada, retornar N/A
    return 'N/A'


def _format_applied_parts(parts) -> str:
    """Formatea las partes aplicadas."""
    if not parts:
        return 'No se aplicaron refacciones ni consumibles.'
    
    result = []
    for part in parts:
        desc = part.get('description', 'N/A')
        qty = part.get('quantity', 'N/A')
        result.append(f'• {desc}: {qty}')
    
    return '<br/>'.join(result)


def _format_work_time(work_time) -> str:
    """Formatea el tiempo de trabajo."""
    if not work_time:
        return 'N/A'
    
    fecha = work_time.get('fecha', 'N/A')
    entrada = work_time.get('hora_entrada', 'N/A')
    salida = work_time.get('hora_salida', 'N/A')
    total = work_time.get('total_horas', 'N/A')
    
    return f"""
    Fecha: {fecha}<br/>
    Hora Entrada: {entrada}<br/>
    Hora Salida: {salida}<br/>
    Total Horas: {total}
    """.strip()
