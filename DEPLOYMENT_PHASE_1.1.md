# Deployment Guide - Fase 1.1: Variables de Entorno

## ✅ Cambios Implementados

Esta fase migra todas las credenciales hardcodeadas a variables de entorno para mejorar la seguridad del sistema.

### Archivos Modificados

1. **`app/utils/constants.py`**
   - Migrado `USUARIO` y `CONTRASENA` (Gestión Real) a env vars
   - Migrado `EVOLUTION_API_KEY` y `EVOLUTION_INSTANCE_NAME` a env vars
   - Agregados fallbacks para URLs

2. **`app/services/splynx_services_singleton.py`**
   - Migrado credenciales de Splynx (`user`, `password`) a env vars
   - Agregada configuración SSL desde env var `SPLYNX_SSL_VERIFY`
   - Agregado warning cuando SSL está deshabilitado

3. **`app/utils/config.py`**
   - Agregado `load_dotenv()` para cargar variables de entorno

### Archivos Nuevos

1. **`.env.template`**: Template para configuración (documentación)
2. **`.env.example`**: Ejemplo con valores reales (NO commitear, solo para referencia)
3. **`validate_env.py`**: Script de validación de variables de entorno

### Dependencias Agregadas

- `python-dotenv==1.2.1`

---

## 🚀 Pasos de Deployment

### Pre-Deployment (Local)

1. **Verificar que todas las pruebas pasen:**
   ```bash
   # Validar variables de entorno
   poetry run python validate_env.py

   # Verificar imports
   poetry run python -c "from app.utils.constants import USUARIO, CONTRASENA, EVOLUTION_API_KEY; print('✅ OK')"
   ```

2. **Verificar que no hay credenciales hardcodeadas:**
   ```bash
   git grep -E "(RoxZ3008|Ronald2025|636A734D58DC)" app/
   # Debe retornar: nada (sin resultados)
   ```

3. **Crear backup del código actual en el servidor:**
   ```bash
   ssh root@190.7.234.37
   cd /opt/splynx-tickets
   tar -czf backup_pre_phase_1.1_$(date +%Y%m%d_%H%M%S).tar.gz .
   ```

---

### Deployment al Servidor

#### Opción A: Deployment Manual (Recomendado para Primera Vez)

1. **SSH al servidor:**
   ```bash
   ssh root@190.7.234.37
   cd /opt/splynx-tickets
   ```

2. **Pull de los cambios:**
   ```bash
   git pull origin main
   ```

3. **Crear archivo .env con las credenciales:**
   ```bash
   # Copiar desde el template
   cp .env.template .env

   # Editar con las credenciales reales
   nano .env
   ```

   **IMPORTANTE:** Configurar estos valores en el archivo `.env`:
   ```env
   SECRET_KEY=<generar una clave secreta fuerte>

   DB_HOST=190.7.234.37
   DB_PORT=3025
   DB_NAME=ipnext
   DB_USER=mysql
   DB_PASSWORD=1234

   SPLYNX_BASE_URL=https://splynx.ipnext.com.ar
   SPLYNX_USER=Ronald
   SPLYNX_PASSWORD=Ronald2025!
   SPLYNX_SSL_VERIFY=False

   GESTION_REAL_USERNAME=RoxZ3008
   GESTION_REAL_PASSWORD=RoxZG3008$
   GESTION_REAL_LOGIN_URL=https://gestionreal.com.ar/login/main_login.php
   GESTION_REAL_CASOS_URL=https://gestionreal.com.ar/index.php?menuitem=10

   EVOLUTION_API_BASE_URL=https://ipnext-evolution-api.s2vvnr.easypanel.host
   EVOLUTION_API_KEY=636A734D58DC-4FD7-B49E-A7DD92EA402E
   EVOLUTION_INSTANCE_NAME=test21

   DEVICE_ANALYSIS_API_URL=http://190.7.234.37:7444
   SESSION_COOKIE_SECURE=False
   ```

4. **Validar el archivo .env:**
   ```bash
   # Verificar que el archivo existe y tiene las variables
   docker-compose exec backend python validate_env.py
   ```

5. **Rebuild y restart de los contenedores:**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

6. **Verificar logs:**
   ```bash
   docker-compose logs -f backend | head -50
   ```

   **Buscar estos mensajes:**
   - ✅ `SplynxServicesSingleton initialized (singleton)`
   - ✅ `Splynx token obtained successfully`
   - ⚠️ Si aparece: `SSL verification is disabled` (esperado con `SPLYNX_SSL_VERIFY=False`)

---

#### Opción B: Deployment Automático (GitHub Actions)

1. **Agregar archivo .env en el servidor ANTES de hacer push:**
   ```bash
   ssh root@190.7.234.37
   cd /opt/splynx-tickets

   # Crear .env si no existe
   if [ ! -f .env ]; then
       cp .env.template .env
       nano .env  # Configurar valores
   fi
   ```

2. **Push de los cambios:**
   ```bash
   git push origin main
   ```

3. **GitHub Actions ejecutará automáticamente:**
   - Pull del código
   - Build de las imágenes
   - Restart de los contenedores

4. **Verificar deployment:**
   ```bash
   ssh root@190.7.234.37
   cd /opt/splynx-tickets
   docker-compose logs -f backend | head -50
   ```

---

## ✅ Post-Deployment Verification

### 1. Health Check
```bash
curl http://localhost:7842/health
# Debe retornar: OK
```

### 2. Verificar Integraciones

**Splynx API:**
```bash
docker-compose exec backend python -c "
from app.services.splynx_services_singleton import SplynxServicesSingleton
service = SplynxServicesSingleton()
print('✅ Splynx connected:', service.token is not None)
"
```

**Gestión Real (Selenium):**
```bash
# Verificar que las credenciales están disponibles
docker-compose exec backend python -c "
from app.utils.constants import USUARIO, CONTRASENA
print('✅ Gestión Real credentials:', USUARIO is not None and CONTRASENA is not None)
"
```

**Evolution API (WhatsApp):**
```bash
docker-compose exec backend python -c "
from app.utils.constants import EVOLUTION_API_KEY, EVOLUTION_INSTANCE_NAME
print('✅ Evolution API configured:', EVOLUTION_API_KEY is not None)
"
```

### 3. Verificar Funcionalidad Crítica

**Test Login:**
```bash
curl -X POST http://localhost:7842/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<password>"}'
```

**Test Scheduler:**
```bash
# Verificar logs del scheduler
docker-compose logs backend | grep "SCHEDULER"
# Debe mostrar: "⏰ SCHEDULER INICIADO"
```

### 4. Monitorear por 24 Horas

```bash
# Logs en vivo
docker-compose logs -f backend

# Verificar errores
docker-compose logs backend | grep -i "error\|exception\|fail" | tail -20
```

---

## 🔄 Rollback Procedure

Si algo sale mal:

### Opción 1: Restaurar Backup
```bash
ssh root@190.7.234.37
cd /opt/splynx-tickets

# Detener contenedores
docker-compose down

# Restaurar backup
tar -xzf backup_pre_phase_1.1_YYYYMMDD_HHMMSS.tar.gz

# Reiniciar
docker-compose up -d
```

### Opción 2: Git Revert
```bash
# Local
git revert <commit-hash>
git push origin main

# Servidor (si manual)
ssh root@190.7.234.37
cd /opt/splynx-tickets
git pull
docker-compose up -d --build
```

---

## 📋 Checklist de Deployment

- [ ] Backup creado: `backup_pre_phase_1.1_*.tar.gz`
- [ ] Archivo `.env` creado en servidor con credenciales reales
- [ ] Variables validadas: `poetry run python validate_env.py` ✅
- [ ] Sin credenciales hardcodeadas: `git grep -E "(RoxZ3008|Ronald2025)"` sin resultados
- [ ] Containers rebuilt: `docker-compose up -d --build`
- [ ] Health check: `curl http://localhost:7842/health` OK
- [ ] Splynx API: Token obtenido ✅
- [ ] Gestión Real: Credenciales cargadas ✅
- [ ] Evolution API: Configuración OK ✅
- [ ] Login funciona: `/api/auth/login` retorna 200
- [ ] Scheduler corriendo: Logs muestran "SCHEDULER INICIADO"
- [ ] Tickets asignándose correctamente
- [ ] WhatsApp enviando notificaciones
- [ ] Sin errores en logs por 24h

---

## 🔒 Seguridad

### Permisos del Archivo .env
```bash
chmod 600 .env
```

### Verificar que .env NO está en Git
```bash
git status
# .env NO debe aparecer en la lista
```

### Generar SECRET_KEY Seguro (Recomendado)
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Usar este valor en .env para SECRET_KEY
```

---

## 📊 Métricas de Éxito

- ✅ 0 credenciales hardcodeadas en código
- ✅ Aplicación arranca sin errores
- ✅ Todas las integraciones funcionan (Splynx, Gestión Real, Evolution API)
- ✅ Scheduler ejecuta jobs cada 3 minutos
- ✅ WhatsApp notifications funcionan
- ✅ Archivo .env NO está en Git

---

## 🆘 Troubleshooting

### Problema: "Variable XX is not defined"
**Solución:** Verificar que el archivo .env existe y tiene la variable:
```bash
cat .env | grep XX
```

### Problema: "No module named 'dotenv'"
**Solución:** Instalar dependencia:
```bash
poetry install
```

### Problema: "SSL Error" en Splynx
**Solución:** Verificar `SPLYNX_SSL_VERIFY=False` en .env

### Problema: Credenciales incorrectas
**Solución:** Verificar valores en .env coinciden con los originales en constants.py (backup)

---

## 📞 Soporte

Si encuentras problemas durante el deployment:

1. Verificar logs: `docker-compose logs backend`
2. Validar .env: `docker-compose exec backend python validate_env.py`
3. Restaurar backup si es crítico
4. Documentar el error para análisis post-mortem

---

**Última actualización:** 2026-02-08
**Fase:** 1.1 - Migración de Credenciales a Variables de Entorno
**Estado:** ✅ Listo para Deployment
