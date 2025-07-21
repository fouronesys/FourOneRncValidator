# Four One RNC Validator

API de verificación de RNCs dominicanos con documentación interactiva, branded como "Four One RNC Validator".

## Características

- ✅ Validación de RNCs dominicanos contra base de datos oficial DGII
- ✅ API REST completa con múltiples endpoints
- ✅ Interfaz web responsiva con Bootstrap
- ✅ Rate limiting integrado (60 req/min)
- ✅ Búsqueda individual y por lotes
- ✅ Documentación interactiva completa
- ✅ Base de datos PostgreSQL para rendimiento óptimo

## Tecnologías

- **Backend**: Flask (Python) + SQLAlchemy ORM
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Data Processing**: Pandas para importación inicial de archivos DGII
- **Deployment**: Gunicorn WSGI server

## Instalación Local

1. Clona el repositorio
2. Instala las dependencias:
   ```bash
   pip install flask pandas gunicorn werkzeug flask-sqlalchemy psycopg2-binary
   ```
3. Configura PostgreSQL y las variables de entorno:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/rnc_validator"
   export SESSION_SECRET="your-secret-key"
   ```
3. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

## Despliegue en Render

### Método 1: Usando render.yaml (Recomendado)

1. Haz fork de este repositorio
2. Conecta tu repositorio a Render
3. Render detectará automáticamente el archivo `render.yaml` y configurará todo

### Método 2: Configuración Manual

1. Crea un nuevo Web Service en Render
2. Conecta tu repositorio GitHub
3. Configuración:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 main:app`
   - **Environment**: Python 3.11

### Variables de Entorno

- `PORT`: Puerto del servidor (automático en Render)
- `SESSION_SECRET`: Clave secreta para sesiones (se genera automáticamente)

## Estructura del Proyecto

```
├── app.py                 # Configuración principal de Flask
├── main.py               # Punto de entrada de la aplicación
├── api_routes.py         # Rutas y endpoints de la API
├── rnc_service.py        # Lógica de negocio para RNCs
├── templates/            # Plantillas HTML
├── static/              # Archivos estáticos (CSS, JS)
├── attached_assets/     # Archivo de datos DGII
├── render.yaml          # Configuración para Render
└── Procfile             # Configuración de proceso
```

## API Endpoints

- `GET /api/validate/{rnc}` - Validar si un RNC existe
- `GET /api/info/{rnc}` - Obtener información completa del RNC
- `POST /api/search` - Búsqueda por lotes (hasta 10 RNCs)
- `GET /api/status` - Estado de la API y estadísticas

## Documentación

Una vez desplegada, visita `/docs` para ver la documentación completa de la API con ejemplos y especificaciones técnicas.

## Datos

La aplicación utiliza el archivo oficial de RNCs de la DGII (Dirección General de Impuestos Internos) de República Dominicana. Los datos se cargan en memoria al inicio de la aplicación para búsquedas rápidas.

## Rate Limiting

- Endpoints GET: 60 requests/minuto por IP
- Endpoint POST: 30 requests/minuto por IP
- Búsqueda por lotes: Máximo 10 RNCs por request

## Contacto

Desarrollado por Four One Technologies.