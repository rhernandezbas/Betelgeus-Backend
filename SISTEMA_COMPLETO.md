# Sistema Completo de Gestión de Tickets - Documentación

## 🚀 Acceso al Sistema

### URL Principal
```
http://190.7.234.37:7842
```

### Credenciales por Defecto

**Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`
- Acceso: Panel completo de administración

**⚠️ IMPORTANTE:** Cambiar la contraseña después del primer login

---

## 📊 Funcionalidades Implementadas

### 1. **Sistema de Autenticación**
- ✅ Login con usuario y contraseña
- ✅ Sesiones seguras
- ✅ Roles: Admin y Operador
- ✅ Protección de rutas según rol
- ✅ Logout con limpieza de sesión

### 2. **Panel de Administración (Solo Admin)**

#### Dashboard
- Vista general del sistema
- Tickets sin resolver y vencidos
- Tiempo promedio de respuesta
- Distribución de tickets por operador
- Gráficos en tiempo real

#### Operadores
- Ver todos los operadores
- Pausar/Reanudar operadores
- Activar/Desactivar operadores
- Habilitar/Deshabilitar notificaciones WhatsApp
- Ver horarios y estadísticas

#### Horarios (Editable)
- ✅ **Crear** nuevos horarios para operadores
- ✅ **Editar** horarios existentes
- ✅ **Eliminar** horarios
- ✅ Múltiples horarios por día
- ✅ Activar/desactivar horarios
- Organizado por día de la semana

#### Mensajes WhatsApp
- Ver plantillas de mensajes
- Copiar mensajes para referencia
- Ver variables disponibles
- Ejemplos de uso

#### Métricas y Reportes
- ✅ **Filtros por fecha** (desde/hasta)
- ✅ Filtros por estado, prioridad, operador
- ✅ **Exportar a CSV**
- ✅ Gráficos de distribución
- ✅ KPIs en tiempo real
- ✅ Lista detallada de tickets
- Análisis de rendimiento

#### Configuración
- Pausar/Reanudar sistema completo
- Reiniciar contadores round-robin
- Ver configuración actual
- Modificar parámetros del sistema

#### Auditoría
- Registro completo de cambios
- Filtros por acción, entidad, usuario
- Valores antes/después de cambios
- IP y timestamp de cada acción

### 3. **Vista de Operador (Solo Lectura)**

Acceso: `http://190.7.234.37:7842/operator-view`

- Ver estado actual (activo/pausado)
- Ver tickets asignados
- Ver horarios de trabajo
- Estadísticas personales
- KPIs individuales
- Actualización automática cada 30 segundos

**Nota:** Los operadores NO pueden modificar nada, solo visualizar

---

## 👥 Gestión de Usuarios

### Crear Usuario Operador

1. Login como admin
2. Ir a la página de gestión de usuarios (próximamente en el menú)
3. O usar el endpoint API:

```bash
curl -X POST http://190.7.234.37:7842/api/auth/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "operador1",
    "password": "password123",
    "full_name": "Nombre del Operador",
    "email": "operador@example.com",
    "role": "operator",
    "person_id": 1
  }'
```

### Modificar Usuario

```bash
curl -X PUT http://190.7.234.37:7842/api/auth/users/2 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Nuevo Nombre",
    "password": "nueva_password"
  }'
```

### Eliminar Usuario

```bash
curl -X DELETE http://190.7.234.37:7842/api/auth/users/2
```

---

## 🔧 Endpoints API Principales

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/auth/me` - Usuario actual
- `POST /api/auth/change-password` - Cambiar contraseña

### Usuarios (Solo Admin)
- `GET /api/auth/users` - Listar usuarios
- `POST /api/auth/users` - Crear usuario
- `PUT /api/auth/users/:id` - Actualizar usuario
- `DELETE /api/auth/users/:id` - Eliminar usuario

### Operadores
- `GET /api/admin/operators` - Listar operadores
- `PUT /api/admin/operators/:id` - Actualizar operador
- `POST /api/admin/operators/:id/pause` - Pausar operador
- `POST /api/admin/operators/:id/resume` - Reanudar operador

### Horarios
- `GET /api/admin/schedules` - Listar horarios
- `POST /api/admin/schedules` - Crear horario
- `PUT /api/admin/schedules/:id` - Actualizar horario
- `DELETE /api/admin/schedules/:id` - Eliminar horario

### Mensajes
- `GET /api/messages/templates` - Listar plantillas
- `GET /api/messages/templates/:key` - Obtener plantilla
- `PUT /api/messages/templates/:id` - Actualizar plantilla

### Métricas
- `GET /api/admin/metrics` - Obtener métricas generales
- `GET /api/admin/dashboard` - Datos del dashboard

---

## 📁 Estructura del Proyecto

```
app_splynx/
├── app/
│   ├── models/
│   │   └── models.py              # Modelos: User, OperatorConfig, etc.
│   ├── interface/
│   │   ├── interfaces.py          # Interfaces CRUD
│   │   ├── users.py               # Interface de usuarios
│   │   └── message_templates.py   # Interface de mensajes
│   ├── routes/
│   │   ├── admin_routes.py        # Rutas de administración
│   │   ├── auth_routes.py         # Rutas de autenticación
│   │   └── messages_routes.py     # Rutas de mensajes
│   └── __init__.py                # Factory de la app
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Login.jsx          # Página de login
│       │   ├── Dashboard.jsx      # Dashboard principal
│       │   ├── Operators.jsx      # Gestión de operadores
│       │   ├── SchedulesEditable.jsx  # Horarios editables
│       │   ├── Messages.jsx       # Mensajes WhatsApp
│       │   ├── Metrics.jsx        # Métricas y reportes
│       │   ├── OperatorView.jsx   # Vista de operador
│       │   └── Configuration.jsx  # Configuración
│       └── components/
│           ├── ProtectedRoute.jsx # Protección de rutas
│           └── Layout.jsx         # Layout con menú
├── migrations/
│   ├── create_admin_tables.sql    # Tablas del panel
│   └── create_users_table.sql     # Tabla de usuarios
└── create_admin_user.py           # Script para crear admin
```

---

## 🔐 Seguridad

- ✅ Contraseñas hasheadas con Werkzeug
- ✅ Sesiones seguras con Flask
- ✅ Protección de rutas por rol
- ✅ Validación de permisos en backend
- ✅ Auditoría completa de acciones
- ✅ Logout con limpieza de sesión

---

## 📝 Próximos Pasos Sugeridos

1. **Página de Gestión de Usuarios en el Frontend**
   - Agregar interfaz visual para crear/editar usuarios
   - Asignar operadores a usuarios

2. **Endpoints de Tickets**
   - Crear endpoints para listar tickets reales
   - Filtros avanzados
   - CRUD completo de tickets

3. **Notificaciones en Tiempo Real**
   - WebSockets para actualizaciones en vivo
   - Notificaciones push

4. **Reportes Avanzados**
   - Gráficos de tendencias
   - Comparativas por período
   - Exportar a PDF

5. **Cambio de Contraseña desde el Frontend**
   - Formulario de cambio de contraseña
   - Validación de contraseña segura

---

## 🐛 Troubleshooting

### El login no funciona
- Verificar que el usuario admin existe: `docker compose exec backend python3 create_admin_user.py`
- Verificar logs del backend: `docker compose logs backend`

### No se ven los datos
- Verificar que el backend está corriendo: `docker compose ps`
- Verificar conexión a la base de datos
- Revisar logs: `docker compose logs backend --tail=50`

### Error de CORS
- Verificar que el frontend está configurado correctamente
- El API_BASE_URL debe ser relativo (vacío) en producción

---

## 📞 Contacto y Soporte

Para cualquier duda o problema:
1. Revisar los logs: `docker compose logs`
2. Verificar el estado: `docker compose ps`
3. Reiniciar servicios: `docker compose restart`

---

## ✅ Checklist de Funcionalidades

- [x] Sistema de autenticación
- [x] Login/Logout
- [x] Roles (Admin/Operador)
- [x] Dashboard con métricas
- [x] Gestión de operadores
- [x] Horarios editables (crear/editar/eliminar)
- [x] Mensajes WhatsApp
- [x] Página de métricas con filtros
- [x] Exportar a CSV
- [x] Vista de operador (solo lectura)
- [x] Configuración del sistema
- [x] Auditoría completa
- [x] Protección de rutas
- [x] Gestión de usuarios (API)
- [ ] Gestión de usuarios (Frontend)
- [ ] CRUD de tickets
- [ ] Cambio de contraseña (Frontend)
- [ ] Notificaciones en tiempo real

---

**Fecha de última actualización:** 14 de Enero, 2026
**Versión:** 2.0.0
