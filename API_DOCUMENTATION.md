# ATTA MONTACARGAS API - Documentación para Frontend

## Información General

- **URL Base**: `http://localhost:8000` (desarrollo) 
- **Documentación Interactiva**: `http://localhost:8000/docs`
- **Esquema OpenAPI**: `http://localhost:8000/openapi.json`
- **Versión**: 1.0.0

## Autenticación

### Sistema de Autenticación JWT

Todos los endpoints (excepto login y root) requieren autenticación mediante JWT Bearer Token.

#### Headers Requeridos
```javascript
headers: {
  'Authorization': 'Bearer <token>',
  'Content-Type': 'application/json'
}
```

### Login
```
POST /api/auth/login
```

**Request:**
```json
{
  "email": "admin@attamontacargas.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Obtener Usuario Actual
```
GET /api/auth/me
```

**Response:**
```json
{
  "id": 1,
  "name": "Jose Alfredo Gonzalez Trigueros",
  "email": "admin@attamontacargas.com",
  "role": "admin",
  "position": "Administrador General",
  "avatar": null,
  "is_active": true,
  "created_at": "2025-08-09T20:25:36.957689Z",
  "updated_at": null
}
```

## Roles de Usuario

- **admin**: Acceso completo al sistema
- **jefe**: Puede ver todos los reportes y aprobarlos
- **operador**: Solo puede ver y editar sus propios reportes

## Endpoints Principales

### 1. Usuarios (`/api/users/`)

#### Listar Usuarios (Solo Admin)
```
GET /api/users/
```

#### Obtener Usuario por ID
```
GET /api/users/{user_id}
```

#### Crear Usuario (Solo Admin)
```
POST /api/users/
```

**Request:**
```json
{
  "name": "Nombre Completo",
  "email": "email@example.com",
  "password": "password123",
  "role": "operador",
  "position": "Técnico de Servicio",
  "avatar": null
}
```

#### Actualizar Usuario
```
PUT /api/users/{user_id}
```

#### Eliminar Usuario (Solo Admin)
```
DELETE /api/users/{user_id}
```

### 2. Clientes (`/api/clients/`)

#### Listar Clientes
```
GET /api/clients/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Industrial Solutions S.A. de C.V.",
    "address": "Av. Industrial #123, Zona Industrial, Guadalajara, Jalisco",
    "created_at": "2025-08-09T20:25:37.675589Z",
    "updated_at": null,
    "contacts": [
      {
        "id": 1,
        "client_id": 1,
        "name": "Juan Pérez",
        "position": "Gerente de Mantenimiento",
        "phone": "3312345678",
        "email": "juan@empresa1.com",
        "created_at": "2025-08-09T20:25:37.679200Z"
      }
    ]
  }
]
```

#### Crear Cliente
```
POST /api/clients/
```

**Request:**
```json
{
  "name": "Nombre de la Empresa",
  "address": "Dirección completa"
}
```

#### Obtener Contactos del Cliente
```
GET /api/clients/{client_id}/contacts
```

#### Crear Contacto para Cliente
```
POST /api/clients/{client_id}/contacts
```

**Request:**
```json
{
  "name": "Nombre del Contacto",
  "position": "Puesto",
  "phone": "1234567890",
  "email": "contacto@empresa.com"
}
```

### 3. Equipos (`/api/equipment/`)

#### Listar Equipos
```
GET /api/equipment/
Query params: ?equipment_type=Eléctrico&skip=0&limit=100
```

**Response:**
```json
[
  {
    "id": 1,
    "type": "Combustión",
    "brand": "Toyota",
    "model": "FG25",
    "serial_number": "TOY-FG25-12345",
    "created_at": "2025-08-09T20:25:37.687101Z",
    "updated_at": null
  }
]
```

#### Crear Equipo
```
POST /api/equipment/
```

**Request:**
```json
{
  "type": "Eléctrico",
  "brand": "Yale",
  "model": "ERP030",
  "serial_number": "YAL-ERP030-67890"
}
```

#### Tipos de Equipo Disponibles
```
GET /api/equipment/types/list
```

**Response:**
```json
{
  "types": ["Combustión", "Eléctrico", "Manual", "Otro"]
}
```

### 4. Reportes de Servicio (`/api/service-reports/`)

#### Listar Reportes
```
GET /api/service-reports/
Query params: ?status_filter=pending&client_id=1&technician_id=3&skip=0&limit=100
```

**Response:**
```json
[
  {
    "id": 1,
    "report_number": 1001,
    "date": "2025-01-15",
    "created_by": 3,
    "client_id": 1,
    "requested_by_id": 1,
    "equipment_id": 1,
    "technician_id": 3,
    "service_type": "Preventivo",
    "billing_type": "Facturación",
    "battery_percentage": 85,
    "horometer_readings": {"h1": 1250},
    "work_performed": "Cambio de aceite hidráulico y filtros",
    "detected_damages": "Fuga menor en sistema hidráulico",
    "possible_causes": [{"id": "1", "name": "Desgaste por Vida Util", "selected": true}],
    "activities_performed": "Reemplazo de aceite, inspección general del equipo",
    "operation_points": {
      "velocidad_avance": null,
      "funciones_auxiliares_operando": null,
      "paro_emergencia_especificaciones": null
    },
    "inspection_items": [
      {
        "id": "1",
        "name": "Golpes deformaciones",
        "category": "Estructural",
        "status": "OK",
        "notes": null
      }
    ],
    "technician_comments": "Equipo en buen estado general.",
    "applied_parts": [{"description": "Aceite hidráulico (Lt)", "quantity": 4}],
    "work_time": {
      "date": "2025-01-15",
      "entryTime": "09:30",
      "exitTime": "11:45",
      "totalHours": 2.25
    },
    "status": "completed",
    "pending_reason": null,
    "client_signature": null,
    "technician_signature": null,
    "created_at": "2025-08-09T20:25:37.690506Z",
    "updated_at": null,
    "technician": { /* Objeto User completo */ },
    "client": { /* Objeto Client completo */ },
    "requested_by": { /* Objeto Contact completo */ },
    "equipment": { /* Objeto Equipment completo */ }
  }
]
```

#### Crear Reporte de Servicio
```
POST /api/service-reports/
```

**Request:**
```json
{
  "date": "2025-08-09",
  "client_id": 1,
  "requested_by_id": 1,
  "equipment_id": 1,
  "service_type": "Preventivo",
  "billing_type": "Facturación",
  "battery_percentage": 90,
  "horometer_readings": {"h1": 2500, "h2": 2510},
  "work_performed": "Mantenimiento preventivo general",
  "detected_damages": "Sin daños detectados",
  "possible_causes": [{"id": "1", "name": "Desgaste Normal", "selected": true}],
  "activities_performed": "Inspección completa, limpieza general",
  "operation_points": {
    "velocidad_avance": 12,
    "funciones_auxiliares_operando": "SÍ",
    "paro_emergencia_especificaciones": "SÍ"
  },
  "inspection_items": [
    {
      "id": "estructural_001",
      "name": "GOLPES DEFORMACIONES",
      "category": "ESTRUCTURAL",
      "status": "OK",
      "notes": "Sin problemas detectados"
    }
  ],
  "technician_comments": "Equipo en excelente estado",
  "applied_parts": [{"description": "Filtro de aceite", "quantity": 1}],
  "work_time": {
    "date": "2025-08-09",
    "entryTime": "08:00",
    "exitTime": "10:00",
    "totalHours": 2
  }
}
```

#### Actualizar Reporte
```
PUT /api/service-reports/{report_id}
```

**Request Example (cambiar estado a pendiente):**
```json
{
  "status": "pending",
  "pending_reason": "Esperando aprobación del supervisor para refacciones adicionales"
}
```

**Request Example (aprobar reporte):**
```json
{
  "status": "completed"
}
```

**Validaciones:**
- Solo roles "jefe" y "admin" pueden cambiar el estado de reportes
- Para establecer status "pending" es obligatorio proporcionar `pending_reason`
- No se puede cambiar un reporte "completed" de vuelta a "pending"
- Al completar un reporte, `pending_reason` se limpia automáticamente

**Response:** Objeto ServiceReport actualizado

#### Subir Firma
```
POST /api/service-reports/{report_id}/upload-signature?signature_type=client
```

**Request:** Multipart form data con archivo de imagen

#### Generar PDF
```
GET /api/service-reports/{report_id}/pdf
```

**Response:** Archivo PDF binario

#### Estadísticas del Dashboard
```
GET /api/service-reports/statistics/dashboard
```

**Response:**
```json
{
  "total_reports": 3,
  "pending_reports": 2,
  "completed_reports": 1,
  "client_count": 3,
  "technician_count": 1,
  "equipment_count": 4
}
```

### 5. Catálogo de Inspección (`/api/inspection/`)

#### Obtener Categorías de Inspección
```
GET /api/inspection/categories
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "ESTRUCTURAL",
    "description": "Inspección de elementos estructurales",
    "order_index": 1,
    "is_active": true,
    "created_at": "2025-08-09T20:25:37.701799Z"
  }
]
```

#### Obtener Items por Categoría
```
GET /api/inspection/categories/{category_id}/items
```

#### Obtener Plantillas para Reportes
```
GET /api/inspection/templates/service-report
```

**Response:**
```json
{
  "inspection_categories": {
    "estructural": [
      {
        "id": "estructural_001",
        "name": "GOLPES DEFORMACIONES",
        "category": "ESTRUCTURAL",
        "description": null
      }
    ],
    "ruedas": [...],
    "seguridad": [...],
    "funcionales": [...],
    "fugas_de_aceite": [...]
  },
  "operation_points": {
    "velocidad_avance": {
      "display_name": "Velocidad de avance",
      "field_type": "number",
      "options": null,
      "validation_rules": {"min": 0, "max": 50, "unit": "Km/h"}
    },
    "funciones_auxiliares_operando": {
      "display_name": "Funciones auxiliares operando",
      "field_type": "select",
      "options": ["SÍ", "NO", "N/A"],
      "validation_rules": null
    },
    "paro_emergencia_especificaciones": {
      "display_name": "Paro de emergencia dentro de especificaciones",
      "field_type": "select",
      "options": ["SÍ", "NO", "N/A"],
      "validation_rules": null
    }
  },
  "status_options": {
    "OK": "Funcionando correctamente",
    "N/A": "No aplica",
    "R": "Requiere atención/reparación"
  }
}
```

## Valores Válidos para Enums

### Tipos de Servicio
- "Preventivo"
- "Correctivo"
- "Instalación"
- "Reparación"
- "Otro"

### Tipos de Facturación
- "Facturación"
- "Renta"
- "Garantía"
- "Sin costo"

### Estados de Inspección
- "OK": Funcionando correctamente
- "N/A": No aplica
- "R": Requiere atención/reparación

### Estados de Reporte
- "pending": Pendiente (requiere `pending_reason`)
- "completed": Completado

#### Reglas de Negocio para Estados
- **pending → completed**: ✅ Permitido (automáticamente limpia `pending_reason`)
- **completed → pending**: ❌ No permitido (flujo unidireccional)
- **pending → pending**: ✅ Permitido (puede actualizar `pending_reason`)
- **Validación**: Al establecer status "pending" es obligatorio proporcionar `pending_reason`

### Roles de Usuario
- "admin": Administrador
- "jefe": Supervisor
- "operador": Técnico

## Manejo de Errores

### Códigos de Estado HTTP

- **200**: OK - Operación exitosa
- **201**: Created - Recurso creado exitosamente
- **400**: Bad Request - Error en los datos enviados
  - "pending_reason is required when setting status to 'pending'"
  - "Cannot change completed reports back to pending status"
- **401**: Unauthorized - Token inválido o expirado
- **403**: Forbidden - Sin permisos suficientes
- **404**: Not Found - Recurso no encontrado
- **422**: Validation Error - Error de validación de datos
- **500**: Internal Server Error - Error interno del servidor

### Estructura de Errores

```json
{
  "detail": "Descripción del error"
}
```

### Errores de Validación (422)

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "field required",
      "input": {...}
    }
  ]
}
```

## Paginación

Los endpoints que retornan listas soportan paginación:

```
GET /api/service-reports/?skip=0&limit=50
```

- **skip**: Número de registros a omitir (default: 0)
- **limit**: Número máximo de registros a retornar (default: 100)

## Filtros Comunes

### Reportes de Servicio
- `status_filter`: "pending" | "completed"
- `client_id`: ID del cliente
- `technician_id`: ID del técnico

### Equipos
- `equipment_type`: "Combustión" | "Eléctrico" | "Manual" | "Otro"

## Credenciales de Prueba

```javascript
// Admin
{
  email: "admin@attamontacargas.com",
  password: "password123"
}

// Jefe/Supervisor
{
  email: "jefe@attamontacargas.com", 
  password: "password123"
}

// Operador/Técnico
{
  email: "victorlopez@attamontacargas.com",
  password: "password123"
}
```

## Notas Importantes para Frontend

1. **Tokens JWT**: Duran 72 horas. Implementar renovación automática.

2. **Permisos por Rol**: 
   - Los operadores solo ven sus propios reportes
   - Los jefes pueden aprobar reportes
   - Solo admins pueden gestionar usuarios

3. **Archivos**: Las firmas se suben como multipart/form-data y se retornan URLs

4. **PDF**: El endpoint de PDF retorna un archivo binario, configurar headers apropiados

5. **Validaciones**: El backend valida todos los datos según los schemas definidos

6. **Relaciones**: Los reportes incluyen objetos anidados completos (cliente, técnico, equipo, contacto)

7. **Números de Reporte**: Se asignan automáticamente de forma secuencial

8. **Catálogo Dinámico**: Usar el endpoint de plantillas para obtener la estructura actual de inspección

## Ejemplos de Uso en Frontend

### Autenticación
```javascript
// Login
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { access_token } = await response.json();

// Usar token en requests posteriores
const headers = {
  'Authorization': `Bearer ${access_token}`,
  'Content-Type': 'application/json'
};
```

### Crear Reporte
```javascript
const reportData = {
  date: "2025-08-09",
  client_id: 1,
  requested_by_id: 1,
  equipment_id: 1,
  service_type: "Preventivo",
  billing_type: "Facturación",
  // ... resto de datos
};

const response = await fetch('/api/service-reports/', {
  method: 'POST',
  headers,
  body: JSON.stringify(reportData)
});
```

### Actualizar Estado de Reporte
```javascript
// Marcar como pendiente con razón
const updateData = {
  status: "pending",
  pending_reason: "Esperando aprobación del supervisor para refacciones adicionales"
};

const response = await fetch(`/api/service-reports/${reportId}`, {
  method: 'PUT',
  headers,
  body: JSON.stringify(updateData)
});

// Aprobar reporte (completa automáticamente)
const approveData = {
  status: "completed"
  // pending_reason se limpia automáticamente
};

const response = await fetch(`/api/service-reports/${reportId}`, {
  method: 'PUT',
  headers,
  body: JSON.stringify(approveData)
});
```

### Subir Firma
```javascript
const formData = new FormData();
formData.append('file', signatureFile);

const response = await fetch(`/api/service-reports/${reportId}/upload-signature?signature_type=client`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});
```

### Descargar PDF
```javascript
const response = await fetch(`/api/service-reports/${reportId}/pdf`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const blob = await response.blob();
const url = URL.createObjectURL(blob);
// Crear link de descarga o mostrar en iframe
```
