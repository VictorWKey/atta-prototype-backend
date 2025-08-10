# CHANGELOG - ATTA MONTACARGAS API

## [v1.1.0] - 2025-08-10

### ✨ Nuevas Funcionalidades

#### Gestión Avanzada de Estados de Reportes con Razones de Pendencia

**Nueva propiedad `pending_reason`:**
- Nuevo campo obligatorio para reportes en estado "pending"
- Permite especificar la razón por la cual un reporte está pendiente
- Se limpia automáticamente cuando el reporte se completa

**Reglas de negocio implementadas:**
- ✅ **pending → completed**: Permitido (automáticamente limpia `pending_reason`)
- ❌ **completed → pending**: **NO permitido** (flujo unidireccional)
- ✅ **pending → pending**: Permitido (puede actualizar `pending_reason`)

### 🔧 Cambios Técnicos

#### Base de Datos
- **Nuevo campo**: `pending_reason` (TEXT, nullable) en tabla `service_reports`
- **Migración**: Campo agregado sin afectar datos existentes

#### API Endpoints

**PUT `/api/service-reports/{report_id}`** - Mejorado
```json
// ✅ Marcar como pendiente (REQUIERE pending_reason)
{
  "status": "pending",
  "pending_reason": "Esperando aprobación del supervisor para refacciones adicionales"
}

// ✅ Aprobar reporte (pending_reason se limpia automáticamente)
{
  "status": "completed"
}

// ❌ Error: Intento de regresar completado a pendiente
{
  "status": "pending",
  "pending_reason": "Cualquier razón"
}
// Response: {"detail": "Cannot change completed reports back to pending status"}
```

#### Validaciones Nuevas
- **400 Bad Request**: "pending_reason is required when setting status to 'pending'"
- **400 Bad Request**: "Cannot change completed reports back to pending status"

#### Permisos
- Solo usuarios con rol "jefe" y "admin" pueden cambiar estados de reportes
- Operadores pueden crear reportes, pero no cambiar estados

### 📋 Casos de Uso

#### Flujo Típico de Trabajo
1. **Operador** crea reporte → Estado: automático (no especificado)
2. **Jefe** revisa y marca como pendiente → Debe proporcionar `pending_reason`
3. **Jefe** aprueba reporte → Estado: "completed", `pending_reason`: `null`

#### Ejemplos de Razones de Pendencia
- "Esperando aprobación del supervisor para refacciones adicionales"
- "Pendiente de validación con el cliente"
- "Requiere autorización para trabajo extra"
- "Esperando disponibilidad de repuestos"

### 🔄 Compatibilidad

#### Backward Compatibility
- ✅ **Reportes existentes**: No afectados, `pending_reason` será `null`
- ✅ **API anterior**: Endpoints existentes siguen funcionando
- ✅ **Frontend**: Campo opcional, no rompe funcionalidad existente

#### Datos de Prueba
- **Reporte 1003**: Configurado como ejemplo con estado "pending" y `pending_reason`
- **Reportes 1001, 1002**: Mantienen estado "completed" con `pending_reason: null`

### 📚 Documentación Actualizada

#### Archivos Actualizados
- `API_DOCUMENTATION.md`: Nuevas reglas de negocio y ejemplos
- `openapi-schema.json`: Esquemas actualizados con `pending_reason`
- `CHANGELOG.md`: Este archivo (nuevo)

#### OpenAPI/Swagger
- **Esquemas actualizados**: `ServiceReportCreate`, `ServiceReportUpdate`, `ServiceReportResponse`
- **Documentación interactiva**: `http://localhost:8000/docs` incluye nuevos campos

### 🧪 Testing

#### Casos Probados
- ✅ Crear reporte pendiente con razón
- ✅ Aprobar reporte pendiente (limpia razón automáticamente)  
- ✅ Rechazar cambio de completado a pendiente
- ✅ Validar requisito de razón para estado pendiente

#### Scripts de Prueba
```bash
# Probar validación de flujo unidireccional
curl -X PUT "http://localhost:8000/api/service-reports/2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "pending", "pending_reason": "Test"}'
# Expected: {"detail": "Cannot change completed reports back to pending status"}

# Probar requisito de pending_reason
curl -X PUT "http://localhost:8000/api/service-reports/3" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "pending"}'
# Expected: {"detail": "pending_reason is required when setting status to 'pending'"}
```

### 🎯 Beneficios de Negocio

#### Para Supervisores
- **Trazabilidad**: Registro claro de por qué un reporte está pendiente
- **Control de flujo**: Imposibilidad de regresar reportes completados
- **Comunicación**: Razones claras para el equipo

#### Para Operadores
- **Claridad**: Entienden por qué su reporte está pendiente
- **Seguimiento**: Pueden ver el estado y razón en tiempo real

#### Para Administradores
- **Auditoría**: Historial completo de cambios de estado
- **Reportes**: Análisis de razones comunes de pendencia
- **Mejora de procesos**: Identificación de cuellos de botella

---

## [v1.0.0] - 2025-08-09

### 🚀 Lanzamiento Inicial
- Sistema completo de gestión de reportes de servicio
- Autenticación JWT con roles
- CRUD completo para usuarios, clientes, equipos y reportes
- Generación de PDFs
- Subida de firmas
- Dashboard con estadísticas
