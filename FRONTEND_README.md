# ATTA MONTACARGAS API - Documentación Completa para Frontend

Este repositorio contiene toda la documentación necesaria para integrar el frontend con la API de ATTA MONTACARGAS.

## 📁 Archivos de Documentación

### 1. [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
**Documentación completa de la API**
- Lista de todos los endpoints disponibles
- Ejemplos de requests y responses
- Información de autenticación y autorización
- Códigos de error y manejo de errores
- Credenciales de prueba

### 2. [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md)
**Guía de integración para TypeScript/JavaScript**
- Interfaces TypeScript completas
- Clase de servicio API lista para usar
- Ejemplos de React Hooks
- Utilidades para manejo de errores
- Gestión de localStorage

### 3. [FRONTEND_SETUP.md](./FRONTEND_SETUP.md)
**Configuración de entorno y setup inicial**
- Variables de entorno requeridas
- Configuración de dependencias
- Esquemas de validación con Yup
- Configuración de Axios
- Constantes y mensajes
- Mocks para testing

### 4. [openapi-schema.json](./openapi-schema.json)
**Esquema OpenAPI 3.1 completo**
- Definiciones de todos los schemas
- Especificación completa de endpoints
- Formato estándar para generación automática de clientes

## 🚀 Inicio Rápido

### 1. Documentación Interactiva
La API tiene documentación automática disponible en:
```
http://localhost:8000/docs
```

### 2. Credenciales de Prueba
```javascript
// Administrador
{
  email: "admin@attamontacargas.com",
  password: "password123"
}

// Supervisor/Jefe
{
  email: "jefe@attamontacargas.com", 
  password: "password123"
}

// Técnico/Operador
{
  email: "victorlopez@attamontacargas.com",
  password: "password123"
}
```

### 3. URL Base de la API
```
http://localhost:8000 (desarrollo)
```

## 🔑 Endpoints Principales

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|---------------|
| `/api/auth/login` | POST | Iniciar sesión | No |
| `/api/auth/me` | GET | Usuario actual | Sí |
| `/api/users/` | GET | Lista de usuarios | Sí (Admin) |
| `/api/clients/` | GET | Lista de clientes | Sí |
| `/api/equipment/` | GET | Lista de equipos | Sí |
| `/api/service-reports/` | GET/POST | Reportes de servicio | Sí |
| `/api/service-reports/{id}/pdf` | GET | Generar PDF | Sí |
| `/api/inspection/templates/service-report` | GET | Plantillas de inspección | Sí |

## 📊 Sistema de Roles

### Admin (`admin`)
- Acceso completo al sistema
- Gestión de usuarios
- Acceso a todas las funcionalidades

### Jefe/Supervisor (`jefe`)
- Ver todos los reportes
- Aprobar reportes (cambiar status)
- Acceso a estadísticas globales

### Operador/Técnico (`operador`)
- Solo sus propios reportes
- Crear y editar reportes pendientes
- Estadísticas personales

## 🛡️ Autenticación

### Flujo de Autenticación
1. **Login**: `POST /api/auth/login` con email/password
2. **Respuesta**: JWT token con 72 horas de duración
3. **Uso**: Incluir en header `Authorization: Bearer <token>`
4. **Renovación**: Implementar renovación automática antes del vencimiento

### Ejemplo de Autenticación
```javascript
// 1. Login
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { access_token } = await response.json();

// 2. Usar token en requests
const headers = {
  'Authorization': `Bearer ${access_token}`,
  'Content-Type': 'application/json'
};

// 3. Hacer requests autenticados
const reports = await fetch('/api/service-reports/', { headers });
```

## 📋 Estructura de Datos Principales

### ServiceReport (Reporte de Servicio)
```typescript
interface ServiceReport {
  id: number;
  report_number: number; // Auto-generado
  date: string;
  service_type: 'Preventivo' | 'Correctivo' | 'Instalación' | 'Reparación' | 'Otro';
  billing_type: 'Facturación' | 'Renta' | 'Garantía' | 'Sin costo';
  status: 'pending' | 'completed';
  
  // Relaciones
  client: Client;
  equipment: Equipment;
  technician: User;
  requested_by: Contact;
  
  // Datos técnicos
  battery_percentage?: number;
  horometer_readings: Record<string, number>;
  work_performed?: string;
  detected_damages?: string;
  inspection_items?: InspectionItem[];
  operation_points?: OperationPoints;
  applied_parts?: AppliedPart[];
  work_time?: WorkTime;
  
  // Firmas
  client_signature?: string;
  technician_signature?: string;
}
```

## 🔧 Funcionalidades Clave

### 1. Gestión de Reportes
- ✅ Crear reportes con auto-numeración
- ✅ Actualizar reportes (con permisos)
- ✅ Sistema de inspección por categorías
- ✅ Puntos de operación configurables
- ✅ Subida de firmas digitales
- ✅ Generación de PDF profesional

### 2. Catálogo de Inspección
- ✅ 5 categorías: Estructural, Ruedas, Seguridad, Funcionales, Fugas de Aceite
- ✅ 39 items de inspección predefinidos
- ✅ Estados: OK, N/A, R (Requiere atención)
- ✅ Sistema flexible y configurable

### 3. Gestión de Archivos
- ✅ Subida de firmas (JPEG/PNG, máx 10MB)
- ✅ Generación de PDF con ReportLab
- ✅ Almacenamiento local con opción S3

### 4. Dashboard y Estadísticas
- ✅ Estadísticas por rol
- ✅ Conteos de entidades
- ✅ Filtros y paginación

## ⚠️ Consideraciones Importantes

### Seguridad
- Todos los endpoints requieren autenticación JWT
- Control de acceso basado en roles estricto
- Validación de datos en el backend
- Tokens con expiración de 72 horas

### Performance
- Paginación en listados grandes
- Relaciones optimizadas con joins
- Campos JSON para datos flexibles

### Validación
- Schemas Pydantic para validación automática
- Errores 422 con detalles específicos
- Validación de archivos y tipos de datos

## 🛠️ Herramientas Recomendadas

### Frontend
- **React Query/TanStack Query**: Para manejo de estado del servidor
- **React Hook Form**: Para formularios complejos
- **Yup/Zod**: Para validación de formularios
- **Axios**: Para cliente HTTP
- **Date-fns**: Para manejo de fechas

### Testing
- **MSW (Mock Service Worker)**: Para mocking de API
- **React Testing Library**: Para testing de componentes
- **Jest**: Para testing unitario

### Debugging
- **React DevTools**: Para debugging de componentes
- **Network Tab**: Para inspeccionar requests
- **Postman/Insomnia**: Para testing manual de API

## 📞 Soporte

### Documentación Automática
```
http://localhost:8000/docs - Swagger UI
http://localhost:8000/redoc - ReDoc
http://localhost:8000/openapi.json - Schema JSON
```

### Estado del Sistema
```
GET http://localhost:8000/health - Health check
GET http://localhost:8000/ - Estado general
```

### Logs y Debugging
```bash
# Ver logs de la API
docker logs atta_api

# Ver logs de la base de datos
docker logs atta_postgres

# Conectar a la base de datos
# Adminer: http://localhost:5050
# Sistema: PostgreSQL
# Servidor: postgres
# Usuario: atta_user
# Contraseña: atta_password123
# Base de datos: atta_db
```

## 🎯 Siguiente Pasos

1. **Leer** `API_DOCUMENTATION.md` para familiarizarse con los endpoints
2. **Implementar** la clase de servicio de `FRONTEND_INTEGRATION.md`
3. **Configurar** el entorno según `FRONTEND_SETUP.md`
4. **Probar** los endpoints con las credenciales de prueba
5. **Integrar** paso a paso cada funcionalidad

¡La API está completamente funcional y lista para integración! 🚀
