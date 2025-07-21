# Guía de Despliegue en Render

## Pasos para Desplegar Four One RNC Validator en Render

### 1. Preparación del Repositorio

Asegúrate de que tu repositorio contenga estos archivos:

- ✅ `render.yaml` - Configuración automática de Render
- ✅ `Procfile` - Comando de inicio alternativo
- ✅ `runtime.txt` - Versión de Python
- ✅ `app.py` - Aplicación Flask principal
- ✅ `main.py` - Punto de entrada
- ✅ `rnc_service.py` - Servicio de datos RNC
- ✅ `api_routes.py` - Rutas de la API
- ✅ `attached_assets/DGII_RNC_1753101730023.TXT` - Archivo de datos

### 2. Configuración en Render

#### Opción A: Usando render.yaml (Automático)

1. Haz fork de este repositorio o sube el código a tu GitHub
2. Ve a [render.com](https://render.com) y regístrate/inicia sesión
3. Haz clic en "New +" → "Blueprint"
4. Conecta tu repositorio GitHub
5. Render detectará automáticamente el `render.yaml` y creará:
   - Web Service (aplicación Flask)
   - PostgreSQL Database (base de datos)

#### Opción B: Configuración Manual

1. Ve a [render.com](https://render.com)
2. Crear la base de datos primero:
   - Haz clic en "New +" → "PostgreSQL"
   - Name: `four-one-rnc-db`
   - Database: `rnc_validator`
   - User: `rnc_user`
3. Crear el Web Service:
   - Haz clic en "New +" → "Web Service"
   - Conecta tu repositorio GitHub
   - Configuración:
     - **Name**: `four-one-rnc-validator`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install flask pandas gunicorn werkzeug flask-sqlalchemy psycopg2-binary`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 main:app`
   - En Environment Variables, conecta la base de datos creada anteriormente

### 3. Variables de Entorno

Render configurará automáticamente:
- `PORT` - Puerto del servidor (automático)
- `SESSION_SECRET` - Clave secreta (se genera automáticamente)
- `FLASK_ENV` - Establecido en "production"

### 4. Verificación del Despliegue

Una vez desplegado, tu aplicación estará disponible en:
`https://four-one-rnc-validator.onrender.com`

### 5. Endpoints de Prueba

Prueba estos endpoints para verificar que funciona:

```bash
# Estado de la API
curl https://tu-app.onrender.com/api/status

# Validar un RNC
curl https://tu-app.onrender.com/api/validate/03100968449

# Información completa
curl https://tu-app.onrender.com/api/info/03100968449
```

### 6. Características del Plan Free

- ✅ 750 horas de cómputo por mes
- ✅ SSL/TLS automático
- ✅ Subdomain .onrender.com
- ⚠️ La aplicación se duerme después de 15 minutos de inactividad
- ⚠️ Primer arranque puede tomar 30-60 segundos (carga de datos)

### 7. Optimizaciones para Producción

El código ya incluye optimizaciones para Render:

- Puerto dinámico usando `$PORT`
- Logging configurado para producción
- Timeout extendido para carga inicial de datos
- Worker único para conservar memoria
- Configuración de proxy para HTTPS

### 8. Solución de Problemas

#### Error: "Application failed to respond"
- Revisa que el archivo de datos esté en `attached_assets/`
- Verifica los logs en el dashboard de Render

#### Error: "Build failed"
- Asegúrate de que las dependencias estén correctas
- Verifica que Python 3.11 esté especificado

#### Tiempo de carga largo
- Es normal en el primer arranque (carga 700k+ registros)
- Considera upgrade a plan paid para mejor rendimiento

### 9. Monitoreo

- Dashboard de Render muestra métricas de CPU/memoria
- Logs están disponibles en tiempo real
- Health checks automáticos en `/api/status`

### 10. Actualizaciones

Para actualizar:
1. Haz push a tu repositorio GitHub
2. Render redesplegará automáticamente
3. Zero-downtime deployment

## Contacto

Si tienes problemas con el despliegue, revisa la documentación de Render o contacta al equipo de desarrollo.