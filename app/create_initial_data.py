from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from core.config import settings
from core.security import get_password_hash
from models import (
    Base, User, Client, Contact, Equipment, ServiceReport,
    InspectionCategory, InspectionItemTemplate, OperationPointTemplate
)
from inspection_data import get_inspection_categories, get_operation_points_templates
import json
import time
import sys

def wait_for_database(max_retries=30, delay=2):
    """Wait for database to be available with retries."""
    for attempt in range(max_retries):
        try:
            # Try to create a connection to test database availability
            engine = create_engine(settings.database_url)
            connection = engine.connect()
            connection.close()
            print(f"✓ Database connection successful on attempt {attempt + 1}")
            return True
        except OperationalError as e:
            if "could not translate host name" in str(e) or "Name or service not known" in str(e):
                print(f"Database not ready (attempt {attempt + 1}/{max_retries}), waiting {delay}s...")
                time.sleep(delay)
            else:
                print(f"Database error: {e}")
                raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    print(f"Failed to connect to database after {max_retries} attempts")
    return False

def create_inspection_catalog(db):
    """Create inspection catalog data using comprehensive data from inspection_data.py"""
    
    # Get comprehensive inspection data
    categories_data = get_inspection_categories()
    operation_points_templates = get_operation_points_templates()
    
    # Create inspection categories
    categories = {}
    for cat_data in categories_data:
        category = InspectionCategory(
            name=cat_data["name"],
            description=cat_data["description"],
            order_index=cat_data["order_index"]
        )
        db.add(category)
        db.flush()  # Get category ID
        categories[cat_data["name"]] = category.id
        
        # Create inspection items for this category
        for item_data in cat_data["items"]:
            item = InspectionItemTemplate(
                category_id=category.id,
                name=item_data["name"],
                description=item_data["description"],
                order_index=item_data["order_index"]
            )
            db.add(item)
    
    # Create operation points templates
    for op_data in operation_points_templates:
        op_template = OperationPointTemplate(
            name=op_data["name"],
            display_name=op_data["display_name"],
            field_type=op_data["field_type"],
            options=op_data.get("options"),
            validation_rules=op_data.get("validation_rules"),
            order_index=op_data["order_index"]
        )
        db.add(op_template)
    
    db.commit()
    print("✓ Comprehensive inspection catalog created")


def create_initial_data():
    """Create initial data for the ATTA MONTACARGAS system."""
    
    # Wait for database to be ready
    if not wait_for_database():
        print("Exiting due to database connection failure")
        sys.exit(1)
    
    # Create engine and session
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Data already exists, skipping user/client/equipment initialization")
            
            # But check if inspection catalog exists
            if not db.query(InspectionCategory).first():
                print("Creating inspection catalog...")
                create_inspection_catalog(db)
            else:
                print("Inspection catalog already exists")
                
            return
        
        # Create users
        users_data = [
            {
                "name": "Jose Alfredo Gonzalez Trigueros",
                "email": "admin@attamontacargas.com",
                "password": "password123",
                "role": "admin",
                "position": "Administrador General"
            },
            {
                "name": "Omar Ivan Lopez Ramirez",
                "email": "jefe@attamontacargas.com",
                "password": "password123",
                "role": "jefe",
                "position": "Jefe de Servicio"
            },
            {
                "name": "Victor Angel Lopez Romero",
                "email": "victorlopez@attamontacargas.com",
                "password": "password123",
                "role": "operador",
                "position": "Técnico de Servicio"
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                position=user_data["position"],
                is_active=True
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        print("✓ Users created")
        
        # Create clients
        clients_data = [
            {
                "name": "Industrial Solutions S.A. de C.V.",
                "address": "Av. Industrial #123, Zona Industrial, Guadalajara, Jalisco"
            },
            {
                "name": "Logística y Transporte del Norte",
                "address": "Blvd. Transportistas #456, Parque Industrial, Zapopan, Jalisco"
            },
            {
                "name": "Almacenes Modernos de México",
                "address": "Calle Almacén #789, Parque Empresarial, Tlaquepaque, Jalisco"
            }
        ]
        
        clients = []
        for client_data in clients_data:
            client = Client(
                name=client_data["name"],
                address=client_data["address"]
            )
            db.add(client)
            clients.append(client)
        
        db.commit()
        print("✓ Clients created")
        
        # Create contacts
        contacts_data = [
            {
                "client_index": 0,
                "name": "Juan Pérez",
                "position": "Gerente de Mantenimiento",
                "phone": "3312345678",
                "email": "juan@empresa1.com"
            },
            {
                "client_index": 0,
                "name": "María López",
                "position": "Jefa de Operaciones",
                "phone": "3387654321",
                "email": "maria@empresa1.com"
            },
            {
                "client_index": 1,
                "name": "Carlos Gómez",
                "position": "Coordinador de Almacén",
                "phone": "3345678901",
                "email": "carlos@empresa2.com"
            },
            {
                "client_index": 2,
                "name": "Ana Martínez",
                "position": "Supervisora de Planta",
                "phone": "3310987654",
                "email": "ana@empresa3.com"
            }
        ]
        
        contacts = []
        for contact_data in contacts_data:
            contact = Contact(
                client_id=clients[contact_data["client_index"]].id,
                name=contact_data["name"],
                position=contact_data["position"],
                phone=contact_data["phone"],
                email=contact_data["email"]
            )
            db.add(contact)
            contacts.append(contact)
        
        db.commit()
        print("✓ Contacts created")
        
        # Create equipment
        equipment_data = [
            {
                "type": "Combustión",
                "brand": "Toyota",
                "model": "FG25",
                "serial_number": "TOY-FG25-12345"
            },
            {
                "type": "Eléctrico",
                "brand": "Yale",
                "model": "ERP030",
                "serial_number": "YAL-ERP030-67890"
            },
            {
                "type": "Eléctrico",
                "brand": "Crown",
                "model": "FC4500",
                "serial_number": "CRW-FC4500-24680"
            },
            {
                "type": "Combustión",
                "brand": "Mitsubishi",
                "model": "FG18N",
                "serial_number": "MIT-FG18N-13579"
            }
        ]
        
        equipment_list = []
        for equip_data in equipment_data:
            equipment = Equipment(
                type=equip_data["type"],
                brand=equip_data["brand"],
                model=equip_data["model"],
                serial_number=equip_data["serial_number"]
            )
            db.add(equipment)
            equipment_list.append(equipment)
        
        db.commit()
        print("✓ Equipment created")
        
        # Create sample service reports with comprehensive data (COMPLETE with ALL PDF fields)
        reports_data = [
            {
                "date": "2025-01-15",
                "created_by": users[2].id,  # Victor (operador)
                "client_id": clients[0].id,
                "requested_by_id": contacts[0].id,
                "equipment_id": equipment_list[0].id,
                "technician_id": users[2].id,
                "service_type": "Preventivo",
                "billing_type": "Facturación",
                "battery_percentage": 85,
                "horometer_readings": {"h1": 1250, "h2": 1300, "h3": 850, "h4": 1120},
                "equipment_specifications": {
                    "model_year": "2023",
                    "capacity": "2.5 ton",
                    "fuel_type": "GLP",
                    "marca": "Toyota",
                    "modelo": "FG25", 
                    "serie": "TOY-FG25-12345"
                },
                "work_performed": "Reemplazo de espejo retrovisor, cambio de aceite hidráulico, filtros y inspección preventiva completa según especificaciones del fabricante",
                "detected_damages": "Daño de espejo roto - fuga menor en sistema hidráulico en conexiones",
                "possible_causes": [
                    {"id": "1", "name": "Daño Operativo", "selected": False},
                    {"id": "2", "name": "Desgaste por Vida Util", "selected": True},
                    {"id": "3", "name": "Vicio Oculto", "selected": False}
                ],
                "activities_performed": "Cambio de espejo retrovisor, reemplazo de aceite hidráulico, cambio de filtros, reparación de conexiones, inspección general completa del equipo según manual",
                "operation_points": {
                    "velocidad_avance": 12,
                    "funciones_auxiliares_operando": "SÍ",
                    "paro_emergencia_especificaciones": "SÍ",
                    "sistema": "OBJETO DE INSPECCIÓN",
                    "objeto_inspeccion": "Montacargas Toyota FG25"
                },
                "inspection_items": [
                    {
                        "category": "ESTRUCTURAL",
                        "items": [
                            {"id": "1", "name": "GOLPES DEFORMACIONES", "status": "OK", "category": "ESTRUCTURAL", "notes": "Sin daños estructurales visibles"},
                            {"id": "2", "name": "SOLDADURA FISURADAS", "status": "N/A", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "3", "name": "TORNILLERÍA COMPLETA Y FIJA", "status": "OK", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "4", "name": "PARTES SUELTAS/FRACTURADAS", "status": "OK", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "5", "name": "DELANTERAS", "status": "OK", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "6", "name": "TRASERAS", "status": "OK", "category": "ESTRUCTURAL", "notes": None}
                        ]
                    },
                    {
                        "category": "RUEDAS", 
                        "items": [
                            {"id": "7", "name": "TRACCIÓN", "status": "OK", "category": "RUEDAS", "notes": None},
                            {"id": "8", "name": "DIFERENCIAL", "status": "OK", "category": "RUEDAS", "notes": None},
                            {"id": "9", "name": "CAJA POSTERIOR DIRECCIÓN", "status": "OK", "category": "RUEDAS", "notes": None},
                            {"id": "10", "name": "FRENOS", "status": "OK", "category": "RUEDAS", "notes": None}
                        ]
                    },
                    {
                        "category": "SEGURIDAD",
                        "items": [
                            {"id": "11", "name": "EXTINTOR", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "12", "name": "PARO DE EMERGENCIA", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "13", "name": "TORRETA", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "14", "name": "ALARMA DE TRASLADO", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "15", "name": "SILBATO/CLAXON", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "16", "name": "ESPEJO RETROVISOR", "status": "R", "category": "SEGURIDAD", "notes": "Reemplazado por daño operativo"},
                            {"id": "17", "name": "CONECTORES BATERÍA Y GAS", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "18", "name": "INDICADORES", "status": "OK", "category": "SEGURIDAD", "notes": None}
                        ]
                    },
                    {
                        "category": "FUNCIONALES",
                        "items": [
                            {"id": "19", "name": "ELEVACIÓN", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "20", "name": "INCLINACIÓN", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "21", "name": "DESPLAZAMIENTO LATERAL", "status": "N/A", "category": "FUNCIONALES", "notes": "No aplica para este modelo"},
                            {"id": "22", "name": "ACCESORIOS", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "23", "name": "DIRECCIÓN HIDRÁULICA", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "24", "name": "FRENOS", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "25", "name": "FONDO DE ESTACIONAMIENTO", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "26", "name": "FONDO DE 5 HORAS", "status": "OK", "category": "FUNCIONALES", "notes": None}
                        ]
                    },
                    {
                        "category": "FUGAS DE ACEITE",
                        "items": [
                            {"id": "27", "name": "EMERGENCIA EN PISO", "status": "N/A", "category": "FUGAS DE ACEITE", "notes": None},
                            {"id": "28", "name": "MANGUERAS", "status": "R", "category": "FUGAS DE ACEITE", "notes": "Fuga menor en conexiones reparada"},
                            {"id": "29", "name": "CILINDROS DE ELEVACIÓN", "status": "OK", "category": "FUGAS DE ACEITE", "notes": None},
                            {"id": "30", "name": "CILINDROS DE INCLINACIÓN", "status": "OK", "category": "FUGAS DE ACEITE", "notes": None},
                            {"id": "31", "name": "DESPLAZAMIENTO LATERAL", "status": "N/A", "category": "FUGAS DE ACEITE", "notes": "No aplica"},
                            {"id": "32", "name": "ACCESORIOS", "status": "OK", "category": "FUGAS DE ACEITE", "notes": None}
                        ]
                    }
                ],
                "technician_comments": "Equipo operando correctamente después del mantenimiento preventivo. Se realizaron todas las verificaciones según manual del fabricante.",
                "client_observations": "Equipo funcionando correctamente después del servicio. Cliente satisfecho con el trabajo realizado.",
                "applied_parts": [
                    {"type": "refacciones", "description": "Espejo retrovisor", "quantity": "1"},
                    {"type": "consumibles", "description": "Aceite hidráulico", "quantity": "4L"},
                    {"type": "consumibles", "description": "Filtro de aceite", "quantity": "1"}
                ],
                "work_time": {
                    "fecha": "15/01/25", 
                    "hora_entrada": "09:30",
                    "hora_salida": "11:45",
                    "total_horas": 2.25,
                    "tiempo_extra": 0.0
                },
                "signatures": {
                    "client": {
                        "name": "Juan Pérez",
                        "signature_url": "/signatures/client_1001.png",
                        "timestamp": "2025-01-15T11:45:00Z"
                    },
                    "technician": {
                        "name": "Victor Angel Lopez Romero", 
                        "signature_url": "/signatures/tech_1001.png",
                        "timestamp": "2025-01-15T11:50:00Z"
                    }
                },
                "status": "completed"
            },
            {
                "date": "2025-01-16",
                "created_by": users[2].id,  # Victor (operador)
                "client_id": clients[1].id,
                "requested_by_id": contacts[2].id,
                "equipment_id": equipment_list[1].id,
                "technician_id": users[2].id,
                "service_type": "Correctivo",
                "billing_type": "Renta",
                "battery_percentage": 60,
                "horometer_readings": {"h1": 3200, "h2": 3250, "h3": 3180, "h4": 3220},
                "equipment_specifications": {
                    "model_year": "2022",
                    "capacity": "3.0 ton",
                    "fuel_type": "Eléctrico",
                    "marca": "Yale",
                    "modelo": "ERP030",
                    "serie": "YAL-ERP030-67890"
                },
                "work_performed": "Reparación de sistema de elevación y reemplazo completo de cilindro hidráulico principal, cambio de mangueras deterioradas",
                "detected_damages": "Cilindro de elevación dañado con fuga severa, manguera hidráulica deteriorada por desgaste operativo",
                "possible_causes": [
                    {"id": "1", "name": "Daño Operativo", "selected": True},
                    {"id": "2", "name": "Desgaste por Vida Util", "selected": True},
                    {"id": "3", "name": "Vicio Oculto", "selected": False}
                ],
                "activities_performed": "Desmontaje y reemplazo de cilindro hidráulico principal, cambio de manguera dañada, instalación de nuevos sellos, pruebas de funcionamiento y calibración del sistema",
                "operation_points": {
                    "velocidad_avance": 10,
                    "funciones_auxiliares_operando": "SÍ",
                    "paro_emergencia_especificaciones": "SÍ",
                    "sistema": "OBJETO DE INSPECCIÓN",
                    "objeto_inspeccion": "Montacargas Yale ERP030"
                },
                "inspection_items": [
                    {
                        "category": "ESTRUCTURAL",
                        "items": [
                            {"id": "1", "name": "GOLPES DEFORMACIONES", "status": "OK", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "2", "name": "SOLDADURA FISURADAS", "status": "OK", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "3", "name": "TORNILLERÍA COMPLETA Y FIJA", "status": "OK", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "4", "name": "PARTES SUELTAS/FRACTURADAS", "status": "OK", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "5", "name": "DELANTERAS", "status": "OK", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "6", "name": "TRASERAS", "status": "OK", "category": "ESTRUCTURAL", "notes": None}
                        ]
                    },
                    {
                        "category": "RUEDAS", 
                        "items": [
                            {"id": "7", "name": "TRACCIÓN", "status": "OK", "category": "RUEDAS", "notes": None},
                            {"id": "8", "name": "DIFERENCIAL", "status": "N/A", "category": "RUEDAS", "notes": "Equipo eléctrico"},
                            {"id": "9", "name": "CAJA POSTERIOR DIRECCIÓN", "status": "OK", "category": "RUEDAS", "notes": None},
                            {"id": "10", "name": "FRENOS", "status": "OK", "category": "RUEDAS", "notes": None}
                        ]
                    },
                    {
                        "category": "SEGURIDAD",
                        "items": [
                            {"id": "11", "name": "EXTINTOR", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "12", "name": "PARO DE EMERGENCIA", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "13", "name": "TORRETA", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "14", "name": "ALARMA DE TRASLADO", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "15", "name": "SILBATO/CLAXON", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "16", "name": "ESPEJO RETROVISOR", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "17", "name": "CONECTORES BATERÍA Y GAS", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "18", "name": "INDICADORES", "status": "OK", "category": "SEGURIDAD", "notes": None}
                        ]
                    },
                    {
                        "category": "FUNCIONALES",
                        "items": [
                            {"id": "19", "name": "ELEVACIÓN", "status": "R", "category": "FUNCIONALES", "notes": "Reparado - cilindro reemplazado"},
                            {"id": "20", "name": "INCLINACIÓN", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "21", "name": "DESPLAZAMIENTO LATERAL", "status": "N/A", "category": "FUNCIONALES", "notes": "No aplica para este modelo"},
                            {"id": "22", "name": "ACCESORIOS", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "23", "name": "DIRECCIÓN HIDRÁULICA", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "24", "name": "FRENOS", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "25", "name": "FONDO DE ESTACIONAMIENTO", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "26", "name": "FONDO DE 5 HORAS", "status": "OK", "category": "FUNCIONALES", "notes": None}
                        ]
                    },
                    {
                        "category": "FUGAS DE ACEITE",
                        "items": [
                            {"id": "27", "name": "EMERGENCIA EN PISO", "status": "R", "category": "FUGAS DE ACEITE", "notes": "Limpiado después de reparación"},
                            {"id": "28", "name": "MANGUERAS", "status": "R", "category": "FUGAS DE ACEITE", "notes": "Manguera reemplazada"},
                            {"id": "29", "name": "CILINDROS DE ELEVACIÓN", "status": "R", "category": "FUGAS DE ACEITE", "notes": "Cilindro reemplazado - fuga severa reparada"},
                            {"id": "30", "name": "CILINDROS DE INCLINACIÓN", "status": "OK", "category": "FUGAS DE ACEITE", "notes": None},
                            {"id": "31", "name": "DESPLAZAMIENTO LATERAL", "status": "N/A", "category": "FUGAS DE ACEITE", "notes": "No aplica"},
                            {"id": "32", "name": "ACCESORIOS", "status": "OK", "category": "FUGAS DE ACEITE", "notes": None}
                        ]
                    }
                ],
                "technician_comments": "Se reparó cilindro dañado y se reemplazó manguera deteriorada. Equipo operando correctamente después de la reparación completa y calibración del sistema hidráulico.",
                "client_observations": "Problema resuelto satisfactoriamente. Equipo listo para operación normal. Cliente conforme con la reparación.",
                "applied_parts": [
                    {"type": "refacciones", "description": "Cilindro hidráulico de elevación", "quantity": "1"},
                    {"type": "refacciones", "description": "Manguera hidráulica", "quantity": "1"},
                    {"type": "consumibles", "description": "Aceite hidráulico", "quantity": "2L"},
                    {"type": "consumibles", "description": "Sellos hidráulicos", "quantity": "1 kit"}
                ],
                "work_time": {
                    "fecha": "16/01/25",
                    "hora_entrada": "14:00",
                    "hora_salida": "18:30",
                    "total_horas": 4.5,
                    "tiempo_extra": 1.0
                },
                "signatures": {
                    "client": {
                        "name": "Carlos Gómez",
                        "signature_url": "/signatures/client_1002.png",
                        "timestamp": "2025-01-16T18:25:00Z"
                    },
                    "technician": {
                        "name": "Victor Angel Lopez Romero",
                        "signature_url": "/signatures/tech_1002.png", 
                        "timestamp": "2025-01-16T18:30:00Z"
                    }
                },
                "status": "completed"
            },
            {
                "date": "2025-07-08", 
                "created_by": users[1].id,  # Omar (jefe)
                "client_id": clients[2].id,
                "requested_by_id": contacts[3].id,
                "equipment_id": equipment_list[2].id,
                "technician_id": users[2].id,
                "service_type": "Correctivo",
                "billing_type": "Sin costo",
                "battery_percentage": 74,
                "horometer_readings": {"h1": 2694, "h2": 11, "h3": None, "h4": None},
                "equipment_specifications": {
                    "model_year": "2021",
                    "capacity": "1.5 ton",
                    "fuel_type": "Eléctrico",
                    "marca": "Crown",
                    "modelo": "FC4500",
                    "serie": "CRW-FC4500-24680"
                },
                "work_performed": "Reemplazo de espejo retrovisor dañado por impacto operativo",
                "detected_damages": "Daño de espejo rota",
                "possible_causes": [
                    {"id": "1", "name": "Daño Operativo", "selected": True},
                    {"id": "2", "name": "Desgaste por Vida Util", "selected": False},
                    {"id": "3", "name": "Vicio Oculto", "selected": False}
                ],
                "activities_performed": "Cambio de espejo",
                "operation_points": {
                    "velocidad_avance": 12,
                    "funciones_auxiliares_operando": "SÍ", 
                    "paro_emergencia_especificaciones": "SÍ",
                    "sistema": "OBJETO DE INSPECCIÓN",
                    "objeto_inspeccion": "montacargas"
                },
                "inspection_items": [
                    {
                        "category": "ESTRUCTURAL",
                        "items": [
                            {"id": "1", "name": "GOLPES DEFORMACIONES", "status": "OK", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "2", "name": "SOLDADURA FISURADAS", "status": "N/A", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "3", "name": "TORNILLERÍA COMPLETA Y FIJA", "status": "OK", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "4", "name": "PARTES SUELTAS/FRACTURADAS", "status": "R", "category": "ESTRUCTURAL", "notes": "Espejo reparado"},
                            {"id": "5", "name": "DELANTERAS", "status": "OK", "category": "ESTRUCTURAL", "notes": None},
                            {"id": "6", "name": "TRASERAS", "status": "OK", "category": "ESTRUCTURAL", "notes": None}
                        ]
                    },
                    {
                        "category": "RUEDAS",
                        "items": [
                            {"id": "7", "name": "TRACCIÓN", "status": "OK", "category": "RUEDAS", "notes": None},
                            {"id": "8", "name": "DIFERENCIAL", "status": "N/A", "category": "RUEDAS", "notes": "Equipo eléctrico"},
                            {"id": "9", "name": "CAJA POSTERIOR DIRECCIÓN", "status": "OK", "category": "RUEDAS", "notes": None},
                            {"id": "10", "name": "FRENOS", "status": "OK", "category": "RUEDAS", "notes": None}
                        ]
                    },
                    {
                        "category": "SEGURIDAD",
                        "items": [
                            {"id": "11", "name": "EXTINTOR", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "12", "name": "PARO DE EMERGENCIA", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "13", "name": "TORRETA", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "14", "name": "ALARMA DE TRASLADO", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "15", "name": "SILBATO/CLAXON", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "16", "name": "ESPEJO RETROVISOR", "status": "R", "category": "SEGURIDAD", "notes": "Reemplazado"},
                            {"id": "17", "name": "CONECTORES BATERÍA Y GAS", "status": "OK", "category": "SEGURIDAD", "notes": None},
                            {"id": "18", "name": "INDICADORES", "status": "OK", "category": "SEGURIDAD", "notes": None}
                        ]
                    },
                    {
                        "category": "FUNCIONALES",
                        "items": [
                            {"id": "19", "name": "ELEVACIÓN", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "20", "name": "INCLINACIÓN", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "21", "name": "DESPLAZAMIENTO LATERAL", "status": "N/A", "category": "FUNCIONALES", "notes": "No aplica"},
                            {"id": "22", "name": "ACCESORIOS", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "23", "name": "DIRECCIÓN HIDRÁULICA", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "24", "name": "FRENOS", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "25", "name": "FONDO DE ESTACIONAMIENTO", "status": "OK", "category": "FUNCIONALES", "notes": None},
                            {"id": "26", "name": "FONDO DE 5 HORAS", "status": "OK", "category": "FUNCIONALES", "notes": None}
                        ]
                    },
                    {
                        "category": "FUGAS DE ACEITE",
                        "items": [
                            {"id": "27", "name": "EMERGENCIA EN PISO", "status": "N/A", "category": "FUGAS DE ACEITE", "notes": None},
                            {"id": "28", "name": "MANGUERAS", "status": "OK", "category": "FUGAS DE ACEITE", "notes": None},
                            {"id": "29", "name": "CILINDROS DE ELEVACIÓN", "status": "OK", "category": "FUGAS DE ACEITE", "notes": None},
                            {"id": "30", "name": "CILINDROS DE INCLINACIÓN", "status": "OK", "category": "FUGAS DE ACEITE", "notes": None},
                            {"id": "31", "name": "DESPLAZAMIENTO LATERAL", "status": "N/A", "category": "FUGAS DE ACEITE", "notes": "No aplica"},
                            {"id": "32", "name": "ACCESORIOS", "status": "OK", "category": "FUGAS DE ACEITE", "notes": None}
                        ]
                    }
                ],
                "technician_comments": "Equipo operando correctamente",
                "client_observations": "Conforme con el servicio realizado. Equipo funcionando normalmente.",
                "applied_parts": [
                    {"type": "refacciones", "description": "Espejo retrovisor", "quantity": "1"}
                ],
                "work_time": {
                    "fecha": "08/07/25",
                    "hora_entrada": "9:00",
                    "hora_salida": "10:30",
                    "total_horas": 1.5,
                    "tiempo_extra": 0.0
                },
                "signatures": {
                    "client": {
                        "name": "Roberto",
                        "signature_url": "/signatures/client_1003.png",
                        "timestamp": "2025-07-08T10:30:00Z"
                    },
                    "technician": {
                        "name": "Victor Angel Lopez Romero",
                        "signature_url": "/signatures/tech_1003.png",
                        "timestamp": "2025-07-08T10:35:00Z"
                    }
                },
                "status": "pending",
                "pending_reason": "Esperando aprobación del supervisor para refacciones adicionales"
            }
        ]
        
        for report_data in reports_data:
            report = ServiceReport(
                date=report_data["date"],
                created_by=report_data["created_by"],
                client_id=report_data["client_id"],
                requested_by_id=report_data["requested_by_id"],
                equipment_id=report_data["equipment_id"],
                technician_id=report_data["technician_id"],
                service_type=report_data["service_type"],
                billing_type=report_data["billing_type"],
                battery_percentage=report_data["battery_percentage"],
                horometer_readings=report_data["horometer_readings"],
                equipment_specifications=report_data.get("equipment_specifications"),
                work_performed=report_data["work_performed"],
                detected_damages=report_data["detected_damages"],
                possible_causes=report_data["possible_causes"],
                activities_performed=report_data["activities_performed"],
                operation_points=report_data["operation_points"],
                inspection_items=report_data["inspection_items"],
                technician_comments=report_data["technician_comments"],
                client_observations=report_data.get("client_observations"),
                applied_parts=report_data["applied_parts"],
                work_time=report_data["work_time"],
                signatures=report_data.get("signatures"),
                status=report_data["status"],
                pending_reason=report_data.get("pending_reason")
            )
            db.add(report)
        
        db.commit()
        print("✓ Service reports created")
        
        # Create inspection catalog data
        if not db.query(InspectionCategory).first():
            # Categories data
            categories_data = [
                {"name": "ESTRUCTURAL", "description": "Inspección de elementos estructurales", "order_index": 1},
                {"name": "RUEDAS", "description": "Inspección de ruedas y elementos de tracción", "order_index": 2},
                {"name": "SEGURIDAD", "description": "Elementos de seguridad del equipo", "order_index": 3},
                {"name": "FUNCIONALES", "description": "Funciones operativas del equipo", "order_index": 4},
                {"name": "FUGAS DE ACEITE", "description": "Inspección de fugas de aceite", "order_index": 5},
            ]
            
            categories = {}
            for cat_data in categories_data:
                category = InspectionCategory(**cat_data)
                db.add(category)
                db.flush()  # Get the ID
                categories[cat_data["name"]] = category.id
            
            # Inspection items data
            items_data = [
                # ESTRUCTURAL
                {"category_id": categories["ESTRUCTURAL"], "name": "GOLPES DEFORMACIONES", "order_index": 1},
                {"category_id": categories["ESTRUCTURAL"], "name": "TOLVAS/GUARDAS/CUBIERTAS", "order_index": 2},
                {"category_id": categories["ESTRUCTURAL"], "name": "TORNILLERÍA Y HERRAJES", "order_index": 3},
                {"category_id": categories["ESTRUCTURAL"], "name": "CONTRAPESO", "order_index": 4},
                {"category_id": categories["ESTRUCTURAL"], "name": "HORQUILLAS", "order_index": 5},
                {"category_id": categories["ESTRUCTURAL"], "name": "MÁSTIL", "order_index": 6},
                {"category_id": categories["ESTRUCTURAL"], "name": "DIRECCIÓN", "order_index": 7},
                {"category_id": categories["ESTRUCTURAL"], "name": "CHASIS", "order_index": 8},
                {"category_id": categories["ESTRUCTURAL"], "name": "MANGUERAS", "order_index": 9},
                {"category_id": categories["ESTRUCTURAL"], "name": "CADENAS", "order_index": 10},
                {"category_id": categories["ESTRUCTURAL"], "name": "PARTES SUELTAS/FRACTURADAS", "order_index": 11},
                
                # RUEDAS
                {"category_id": categories["RUEDAS"], "name": "DELANTERAS", "order_index": 1},
                {"category_id": categories["RUEDAS"], "name": "DIRECCIONES TRASERAS", "order_index": 2},
                {"category_id": categories["RUEDAS"], "name": "TRACCIÓN", "order_index": 3},
                {"category_id": categories["RUEDAS"], "name": "CASTER (POSTERIOR DERECHA)", "order_index": 4},
                {"category_id": categories["RUEDAS"], "name": "CARGA (AL FRENTE ESTABILIZADORES)", "order_index": 5},
                
                # SEGURIDAD
                {"category_id": categories["SEGURIDAD"], "name": "EXTINGUIDOR", "order_index": 1},
                {"category_id": categories["SEGURIDAD"], "name": "PARO DE EMERGENCIA", "order_index": 2},
                {"category_id": categories["SEGURIDAD"], "name": "TORRETA", "order_index": 3},
                {"category_id": categories["SEGURIDAD"], "name": "ALARMA DE VIAJE", "order_index": 4},
                {"category_id": categories["SEGURIDAD"], "name": "LUCES DE TRABAJO", "order_index": 5},
                {"category_id": categories["SEGURIDAD"], "name": "ESPEJO RETROVISOR", "order_index": 6},
                {"category_id": categories["SEGURIDAD"], "name": "CONECTOR A BATERÍA/GAS", "order_index": 7},
                {"category_id": categories["SEGURIDAD"], "name": "SWICH ENCENDIDO", "order_index": 8},
                
                # FUNCIONALES
                {"category_id": categories["FUNCIONALES"], "name": "ELEVACIÓN", "order_index": 1},
                {"category_id": categories["FUNCIONALES"], "name": "INCLINACIÓN", "order_index": 2},
                {"category_id": categories["FUNCIONALES"], "name": "DESPLAZADOR LATERAL", "order_index": 3},
                {"category_id": categories["FUNCIONALES"], "name": "ACCESORIOS", "order_index": 4},
                {"category_id": categories["FUNCIONALES"], "name": "AVANCE/RETROCESO", "order_index": 5},
                {"category_id": categories["FUNCIONALES"], "name": "FRENADO", "order_index": 6},
                {"category_id": categories["FUNCIONALES"], "name": "FRENO DE ESTACIONAMIENTO", "order_index": 7},
                {"category_id": categories["FUNCIONALES"], "name": "CONTADOR DE HORAS", "order_index": 8},
                
                # FUGAS DE ACEITE
                {"category_id": categories["FUGAS DE ACEITE"], "name": "EVIDENCIA EN PISO", "order_index": 1},
                {"category_id": categories["FUGAS DE ACEITE"], "name": "MANGUERAS Y CONEXIONES", "order_index": 2},
                {"category_id": categories["FUGAS DE ACEITE"], "name": "CILINDROS DE ELEVACIÓN", "order_index": 3},
                {"category_id": categories["FUGAS DE ACEITE"], "name": "CILINDRO DE INCLINACIÓN", "order_index": 4},
                {"category_id": categories["FUGAS DE ACEITE"], "name": "CILINDRO DESPLAZADOR LATERAL", "order_index": 5},
                {"category_id": categories["FUGAS DE ACEITE"], "name": "CILINDROS DE REACH", "order_index": 6},
                {"category_id": categories["FUGAS DE ACEITE"], "name": "ACCESORIOS", "order_index": 7},
            ]
            
            for item_data in items_data:
                item = InspectionItemTemplate(**item_data)
                db.add(item)
            
            # Operation point templates
            operation_points_data = [
                {
                    "name": "velocidad_avance",
                    "display_name": "Velocidad de avance",
                    "field_type": "number",
                    "validation_rules": {"min": 0, "max": 50, "unit": "Km/h"},
                    "order_index": 1
                },
                {
                    "name": "funciones_auxiliares_operando",
                    "display_name": "Funciones auxiliares operando",
                    "field_type": "select",
                    "options": ["SÍ", "NO", "N/A"],
                    "order_index": 2
                },
                {
                    "name": "paro_emergencia_especificaciones",
                    "display_name": "Paro de emergencia dentro de especificaciones",
                    "field_type": "select",
                    "options": ["SÍ", "NO", "N/A"],
                    "order_index": 3
                }
            ]
            
            for op_data in operation_points_data:
                op_template = OperationPointTemplate(**op_data)
                db.add(op_template)
            
            db.commit()
            print("✓ Inspection catalog created")
        
        print("\n🎉 Initial data created successfully!")
        print("\nDefault login credentials:")
        print("Admin: admin@attamontacargas.com / password123")
        print("Jefe: jefe@attamontacargas.com / password123")
        print("Operador: victorlopez@attamontacargas.com / password123")
        
    except Exception as e:
        print(f"Error creating initial data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_data()
