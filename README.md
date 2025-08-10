# ATTA MONTACARGAS - Backend API

Backend profesional para la aplicación móvil de ATTA MONTACARGAS, desarrollado con FastAPI, PostgreSQL y Docker.

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker y Docker Compose instalados
- Git

### Instalación

1. **Clonar el repositorio y navegar al backend**
```bash
cd backend
```

2. **Configurar variables de entorno (opcional)**
```bash
cp .env.example .env
# Editar .env si necesitas configurar AWS S3 u otras variables
```

3. **Levantar todos los servicios**
```bash
docker-compose up -d
```

¡Eso es todo! El backend estará corriendo automáticamente.

## 📋 Servicios Disponibles

| Servicio | URL | Descripción |
|----------|-----|-------------|
| API Principal | http://localhost:8000 | FastAPI backend |
| Documentación | http://localhost:8000/docs | Swagger UI |
| PostgreSQL | localhost:5432 | Base de datos |
| Adminer | http://localhost:5050 | Administrador de BD |

## 🔐 Usuarios por Defecto

| Email | Password | Rol |
|-------|----------|-----|
| admin@attamontacargas.com | password123 | admin |
| jefe@attamontacargas.com | password123 | jefe |
| victorlopez@attamontacargas.com | password123 | operador |

## 🏗️ Arquitectura

### Stack Tecnológico
- **FastAPI**: Framework web moderno y rápido
- **PostgreSQL 15**: Base de datos relacional
- **SQLAlchemy**: ORM para Python
- **Alembic**: Migraciones de base de datos
- **JWT**: Autenticación basada en tokens
- **ReportLab**: Generación de PDFs profesionales
- **Docker**: Containerización

### Estructura del Proyecto
```
backend/
├── app/
│   ├── core/           # Configuración y seguridad
│   ├── models.py       # Modelos SQLAlchemy
│   ├── schemas/        # Schemas Pydantic
│   ├── routers/        # Endpoints REST
│   ├── utils/          # Utilidades (PDF, S3)
│   └── main.py         # Aplicación principal
├── sql/
│   └── init.sql        # Datos iniciales
├── docker-compose.yml  # Orquestación
├── Dockerfile         # Imagen de la aplicación
└── requirements.txt   # Dependencias Python
```

## 🔗 API Endpoints

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Obtener usuario actual

### Usuarios
- `GET /api/users/` - Listar usuarios (admin)
- `POST /api/users/` - Crear usuario (admin)
- `PUT /api/users/{id}` - Actualizar usuario
- `DELETE /api/users/{id}` - Eliminar usuario (admin)

### Clientes
- `GET /api/clients/` - Listar clientes
- `POST /api/clients/` - Crear cliente
- `PUT /api/clients/{id}` - Actualizar cliente
- `GET /api/clients/{id}/contacts` - Contactos del cliente

### Equipos
- `GET /api/equipment/` - Listar equipos
- `POST /api/equipment/` - Crear equipo
- `PUT /api/equipment/{id}` - Actualizar equipo

### Reportes de Servicio
- `GET /api/service-reports/` - Listar reportes
- `POST /api/service-reports/` - Crear reporte
- `PUT /api/service-reports/{id}` - **Actualizar reporte con validaciones de flujo**
- `GET /api/service-reports/{id}/pdf` - Generar PDF
- `POST /api/service-reports/{id}/upload-signature` - Subir firma

### 🔄 **Gestión de Estados con Razones de Pendencia** (Nuevo v1.1.0)
Los reportes ahora incluyen gestión avanzada de estados:

**Estados disponibles:**
- `pending`: Pendiente (requiere `pending_reason`)
- `completed`: Completado

**Reglas de negocio:**
- ✅ **pending → completed**: Permitido (limpia `pending_reason` automáticamente)
- ❌ **completed → pending**: NO permitido (flujo unidireccional)
- ✅ **pending → pending**: Permitido (actualizar razón)

**Ejemplo de uso:**
```bash
# Marcar como pendiente
curl -X PUT "/api/service-reports/1" \
  -d '{"status": "pending", "pending_reason": "Esperando aprobación supervisor"}'

# Aprobar reporte  
curl -X PUT "/api/service-reports/1" \
  -d '{"status": "completed"}'
```
- `POST /api/service-reports/` - Crear reporte
- `PUT /api/service-reports/{id}` - Actualizar reporte
- `GET /api/service-reports/{id}/pdf` - Generar PDF
- `GET /api/service-reports/statistics/dashboard` - Estadísticas

## 🎯 Sistema de Roles

### Operador
- Crear reportes de servicio
- Ver y editar sus propios reportes pendientes
- Generar PDFs de sus reportes

### Jefe
- Ver todos los reportes
- Aprobar reportes (cambiar estado a completado)
- Ver estadísticas generales

### Administrador
- Acceso completo al sistema
- Gestionar usuarios
- Eliminar reportes y equipos
- Configuraciones del sistema

## 💾 Base de Datos

### Modelo de Datos
- **users**: Usuarios del sistema con roles
- **clients**: Empresas cliente
- **contacts**: Contactos de los clientes
- **equipment**: Equipos de montacargas
- **service_reports**: Reportes de servicio (JSON para datos complejos)

### Acceso a Adminer
1. Abrir http://localhost:5050
2. Seleccionar Sistema: `PostgreSQL`
3. Servidor: `postgres`
4. Usuario: `atta_user`
5. Contraseña: `atta_password123`
6. Base de datos: `atta_db`

## 📄 Generación de PDFs

El sistema utiliza **ReportLab** para generar PDFs profesionales que incluyen:
- Logo y colores corporativos de ATTA MONTACARGAS
- Información completa del reporte
- Tablas formateadas para inspección
- Sección de firmas
- Diseño profesional e idéntico al requerido

## ☁️ AWS S3 (Opcional)

Para producción, configura AWS S3 para almacenar:
- Firmas digitales
- Fotos de inspección
- PDFs generados

```env
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_S3_BUCKET=tu-bucket-name
```

## 🔧 Desarrollo

### Comandos Útiles

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Reiniciar solo la API
docker-compose restart api

# Acceder al contenedor de la API
docker-compose exec api bash

# Parar todos los servicios
docker-compose down

# Parar y eliminar volúmenes (⚠️ elimina datos)
docker-compose down -v
```

### Modificar Código
Los archivos en `./app` están montados como volumen, por lo que los cambios se reflejan automáticamente gracias al `--reload` de uvicorn.

## 🧪 Testing

### Probar la API
1. Abrir http://localhost:8000/docs
2. Usar el endpoint `/api/auth/login` con credenciales por defecto
3. Copiar el token de respuesta
4. Hacer clic en "Authorize" y pegar: `Bearer <token>`
5. Probar cualquier endpoint

## 🚨 Solución de Problemas

### Puerto ya en uso
```bash
# Verificar qué usa el puerto
lsof -i :8000
lsof -i :5432

# Cambiar puertos en docker-compose.yml si es necesario
```

### Base de datos no conecta
```bash
# Reiniciar servicios en orden
docker-compose down
docker-compose up -d postgres
docker-compose logs postgres
docker-compose up -d api
```

### Problemas de permisos
```bash
# En Linux/Mac, asegurar permisos
sudo chown -R $USER:$USER .
```

## 📱 Integración con Frontend

### Configuración de la App Móvil
1. Cambiar la URL base en el frontend a `http://localhost:8000/api`
2. Usar fetch en lugar de axios
3. Implementar Context API para auth y datos
4. Mantener JWT en AsyncStorage

### Flujo de Autenticación
```javascript
// Login
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

// Requests autenticados
const response = await fetch('http://localhost:8000/api/service-reports/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

## 🎯 Próximos Pasos

1. **Implementar en la app móvil**:
   - Reemplazar datos mock con llamadas a la API
   - Implementar Context API para estado global
   - Agregar manejo de errores y loading states

2. **Funcionalidades adicionales**:
   - Notificaciones push
   - Sincronización offline
   - Reportes avanzados y analytics
   - Sistema de archivos más robusto

3. **Despliegue en producción**:
   - Configurar AWS/Azure/GCP
   - Implementar CI/CD
   - Configurar monitoring y logs
   - SSL y seguridad adicional

---

**Desarrollado para ATTA MONTACARGAS** 🏗️  
*Expertos en Montacargas*
