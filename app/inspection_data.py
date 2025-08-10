"""
Datos iniciales para el catálogo de inspección basados en el documento PDF de ATTA Montacargas
"""

# Catálogo completo de inspección por categorías (basado en el documento PDF)
INSPECTION_CATEGORIES = [
    {
        "name": "ESTRUCTURAL",
        "description": "Inspección de estructura general del montacargas",
        "order_index": 1,
        "items": [
            {"name": "GOLPES DEFORMACIONES", "description": "Revisión de golpes y deformaciones en la estructura", "order_index": 1},
            {"name": "SOLDADURA FISURADAS", "description": "Inspección de soldaduras con fisuras", "order_index": 2},
            {"name": "TORNILLERÍA COMPLETA Y FIJA", "description": "Verificación de tornillería completa y fija", "order_index": 3},
            {"name": "PARTES SUELTAS / FRACTURADAS", "description": "Detección de partes sueltas o fracturadas", "order_index": 4},
            {"name": "DELANTERAS", "description": "Inspección de partes delanteras", "order_index": 5},
            {"name": "TRASERAS", "description": "Inspección de partes traseras", "order_index": 6},
        ]
    },
    {
        "name": "RUEDAS",
        "description": "Inspección del sistema de ruedas y tracción",
        "order_index": 2,
        "items": [
            {"name": "TRACCIÓN", "description": "Sistema de tracción", "order_index": 1},
            {"name": "DIFERENCIAL", "description": "Sistema diferencial", "order_index": 2},
            {"name": "CAJA POSTERIOR DIRECCIÓN", "description": "Caja posterior de dirección", "order_index": 3},
            {"name": "FRENOS", "description": "Sistema de frenos", "order_index": 4},
            {"name": "EXTINTOR", "description": "Extintor de emergencia", "order_index": 5},
            {"name": "PALO DE EMERGENCIA", "description": "Palo de emergencia", "order_index": 6},
            {"name": "TORRETA", "description": "Sistema de torreta", "order_index": 7},
            {"name": "ALARMA DE TRASLADO", "description": "Alarma de traslado", "order_index": 8},
            {"name": "SILBATO / CLAXON", "description": "Sistema de silbato/claxon", "order_index": 9},
            {"name": "ESPEJO RETROVISIOR", "description": "Espejo retrovisor", "order_index": 10},
            {"name": "CONECTORES BATERÍA Y GAS", "description": "Conectores de batería y gas", "order_index": 11},
            {"name": "INDICADORES", "description": "Tablero de indicadores", "order_index": 12},
        ]
    },
    {
        "name": "SEGURIDAD",
        "description": "Elementos de seguridad del montacargas",
        "order_index": 3,
        "items": [
            {"name": "EMERGENCIA EN PISO", "description": "Paro de emergencia en piso", "order_index": 1},
            {"name": "MANGUERAS", "description": "Estado de mangueras", "order_index": 2},
            {"name": "CILINDROS DE ELEVACIÓN", "description": "Cilindros de elevación", "order_index": 3},
            {"name": "CILINDROS DE INCLINACIÓN", "description": "Cilindros de inclinación", "order_index": 4},
            {"name": "DESPLAZAMIENTO LATERAL", "description": "Sistema de desplazamiento lateral", "order_index": 5},
            {"name": "ACCESORIOS", "description": "Accesorios adicionales", "order_index": 6},
        ]
    },
    {
        "name": "FUNCIONALES",
        "description": "Funciones operacionales del montacargas",
        "order_index": 4,
        "items": [
            {"name": "ELEVACIÓN", "description": "Función de elevación", "order_index": 1},
            {"name": "INCLINACIÓN", "description": "Función de inclinación", "order_index": 2},
            {"name": "DESPLAZAMIENTO LATERAL", "description": "Función de desplazamiento lateral", "order_index": 3},
            {"name": "ACCESORIOS", "description": "Funcionamiento de accesorios", "order_index": 4},
            {"name": "DIRECCIÓN HIDRÁULICA", "description": "Sistema de dirección hidráulica", "order_index": 5},
            {"name": "FRENOS", "description": "Sistema de frenos funcional", "order_index": 6},
            {"name": "FONDO DE ESTACIONAMIENTO", "description": "Fondo de estacionamiento", "order_index": 7},
            {"name": "FONDO DE 5 HORAS", "description": "Fondo de 5 horas", "order_index": 8},
        ]
    },
    {
        "name": "FUGAS_DE_ACEITE",
        "description": "Detección de fugas en el sistema hidráulico",
        "order_index": 5,
        "items": [
            {"name": "TANQUE HIDRÁULICO", "description": "Fugas en tanque hidráulico", "order_index": 1},
            {"name": "BOMBA", "description": "Fugas en bomba", "order_index": 2},
            {"name": "VÁLVULAS", "description": "Fugas en válvulas", "order_index": 3},
            {"name": "MANGUERAS", "description": "Fugas en mangueras", "order_index": 4},
            {"name": "CILINDROS ELEVACIÓN", "description": "Fugas en cilindros de elevación", "order_index": 5},
            {"name": "CILINDROS INCLINACIÓN", "description": "Fugas en cilindros de inclinación", "order_index": 6},
            {"name": "CILINDROS REACH", "description": "Fugas en cilindros reach", "order_index": 7},
            {"name": "ACCESORIOS", "description": "Fugas en accesorios", "order_index": 8},
        ]
    }
]

# Puntos de operación estándar
OPERATION_POINTS_TEMPLATES = [
    {
        "name": "velocidad_avance",
        "display_name": "Velocidad de Avance",
        "field_type": "number",
        "validation_rules": {"min": 0, "max": 50, "unit": "km/h"},
        "order_index": 1
    },
    {
        "name": "funciones_auxiliares_operando",
        "display_name": "Funciones Auxiliares Operando",
        "field_type": "select",
        "options": ["SÍ", "NO", "N/A"],
        "order_index": 2
    },
    {
        "name": "paro_emergencia_especificaciones",
        "display_name": "Paro de Emergencia dentro de Especificaciones",
        "field_type": "select",
        "options": ["SÍ", "NO", "N/A"],
        "order_index": 3
    },
    {
        "name": "sistema",
        "display_name": "Sistema",
        "field_type": "text",
        "order_index": 4
    },
    {
        "name": "objeto_inspeccion",
        "display_name": "Objeto de Inspección",
        "field_type": "text",
        "order_index": 5
    }
]

# Tipos comunes de refacciones y consumibles
COMMON_PARTS = {
    "refacciones": [
        "Espejo retrovisor",
        "Filtro de aceite hidráulico",
        "Filtro de aire",
        "Pastillas de freno",
        "Balatas",
        "Manguera hidráulica",
        "Válvula de alivio",
        "Sello hidráulico",
        "Rodamiento",
        "Cadena de elevación",
        "Uña para montacargas",
        "Llanta sólida",
        "Batería",
        "Motor de tracción",
        "Bomba hidráulica"
    ],
    "consumibles": [
        "Aceite hidráulico",
        "Aceite de motor",
        "Refrigerante",
        "Grasa para rodamientos",
        "Líquido de frenos",
        "Electrolito para batería",
        "Filtro de combustible",
        "Bujías",
        "Fusibles",
        "Focos",
        "Trapos industriales",
        "Limpiador de contactos",
        "Anticorrosivo",
        "Soldadura",
        "Tornillería diversa"
    ]
}

def get_inspection_categories():
    """Retorna las categorías de inspección para poblar la BD"""
    return INSPECTION_CATEGORIES

def get_operation_points_templates():
    """Retorna las plantillas de puntos de operación"""
    return OPERATION_POINTS_TEMPLATES

def get_common_parts():
    """Retorna partes y consumibles comunes"""
    return COMMON_PARTS
