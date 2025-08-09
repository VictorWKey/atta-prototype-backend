from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from core.security import get_password_hash
from models import Base, User, Client, Contact, Equipment, ServiceReport
import json

def create_initial_data():
    """Create initial data for the ATTA MONTACARGAS system."""
    
    # Create engine and session
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Data already exists, skipping initialization")
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
        
        # Create sample service reports
        reports_data = [
            {
                "report_number": 1001,
                "date": "2025-01-15",
                "created_by": users[2].id,  # Victor (operador)
                "client_id": clients[0].id,
                "requested_by_id": contacts[0].id,
                "equipment_id": equipment_list[0].id,
                "technician_id": users[2].id,
                "service_type": "Preventivo",
                "billing_type": "Facturación",
                "battery_percentage": 85,
                "horometer_readings": {"h1": 1250},
                "work_performed": "Cambio de aceite hidráulico y filtros",
                "detected_damages": "Fuga menor en sistema hidráulico",
                "possible_causes": [{"id": "1", "name": "Desgaste por Vida Util", "selected": True}],
                "activities_performed": "Reemplazo de aceite, inspección general del equipo",
                "operation_points": {
                    "speed": 12,
                    "auxiliaryFunctionsOperating": "Sí",
                    "emergencyStop": "Sí"
                },
                "inspection_items": [
                    {"id": "1", "name": "Golpes deformaciones", "status": "OK", "category": "Estructural"},
                    {"id": "2", "name": "Horquillas", "status": "OK", "category": "Estructural"},
                    {"id": "3", "name": "Delanteras", "status": "OK", "category": "Ruedas"}
                ],
                "technician_comments": "Equipo en buen estado general. Se realizó mantenimiento preventivo según especificaciones.",
                "applied_parts": [{"description": "Aceite hidráulico (Lt)", "quantity": 4}],
                "work_time": {
                    "date": "2025-01-15",
                    "entryTime": "09:30",
                    "exitTime": "11:45",
                    "totalHours": 2.25
                },
                "status": "completed"
            },
            {
                "report_number": 1002,
                "date": "2025-01-16",
                "created_by": users[2].id,  # Victor (operador)
                "client_id": clients[1].id,
                "requested_by_id": contacts[2].id,
                "equipment_id": equipment_list[1].id,
                "technician_id": users[2].id,
                "service_type": "Correctivo",
                "billing_type": "Renta",
                "battery_percentage": 60,
                "horometer_readings": {"h1": 3200, "h2": 3250},
                "work_performed": "Reparación de sistema de elevación",
                "detected_damages": "Cilindro de elevación dañado",
                "possible_causes": [{"id": "1", "name": "Daño Operativo", "selected": True}],
                "activities_performed": "Reemplazo de cilindro hidráulico, pruebas de funcionamiento",
                "operation_points": {
                    "speed": 10,
                    "auxiliaryFunctionsOperating": "Sí",
                    "emergencyStop": "Sí"
                },
                "inspection_items": [
                    {"id": "1", "name": "Cilindros de elevación", "status": "R", "category": "Fugas de Aceite"},
                    {"id": "2", "name": "Elevación", "status": "OK", "category": "Funcionales"}
                ],
                "technician_comments": "Se reparó cilindro dañado. Equipo operando correctamente después de la reparación.",
                "applied_parts": [{"description": "Cilindro hidráulico", "quantity": 1}],
                "work_time": {
                    "date": "2025-01-16",
                    "entryTime": "14:00",
                    "exitTime": "17:30",
                    "totalHours": 3.5
                },
                "status": "pending"
            }
        ]
        
        for report_data in reports_data:
            report = ServiceReport(
                report_number=report_data["report_number"],
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
                work_performed=report_data["work_performed"],
                detected_damages=report_data["detected_damages"],
                possible_causes=report_data["possible_causes"],
                activities_performed=report_data["activities_performed"],
                operation_points=report_data["operation_points"],
                inspection_items=report_data["inspection_items"],
                technician_comments=report_data["technician_comments"],
                applied_parts=report_data["applied_parts"],
                work_time=report_data["work_time"],
                status=report_data["status"]
            )
            db.add(report)
        
        db.commit()
        print("✓ Service reports created")
        
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
