# Four One RNC Validator

## Overview

This is a Flask-based web application that provides an API for validating Dominican Republic RNC (Registro Nacional del Contribuyente) numbers. The application serves both a web interface and REST API endpoints for RNC validation and information retrieval.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Application Structure**: Modular design with separate blueprint for API routes
- **Service Layer**: Dedicated RNC service class for data processing and validation
- **Web Server**: WSGI-compatible with ProxyFix middleware for production deployment

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default templating engine)
- **UI Framework**: Bootstrap 5.3.0 for responsive design
- **Icons**: Font Awesome 6.0.0
- **Styling**: Custom CSS with CSS variables and animations
- **JavaScript**: Vanilla JavaScript for client-side interactions

## Key Components

### 1. Application Entry Points
- **app.py**: Main Flask application configuration and setup
- **main.py**: Alternative entry point for running the application
- **api_routes.py**: Blueprint containing all API endpoints and web routes

### 2. RNC Service Layer
- **rnc_service.py**: Core business logic for RNC data processing
  - Handles CSV file loading with multiple encoding support (latin-1, windows-1252, iso-8859-1, utf-8)
  - Manages RNC data validation and lookup operations
  - Uses pandas for efficient data manipulation

### 3. Rate Limiting System
- **Implementation**: In-memory rate limiting using Python dictionaries
- **Limit**: 60 requests per minute per IP address
- **Production Note**: Designed to be replaced with Redis or similar for scalability

### 4. Frontend Components
- **Templates**: HTML templates for main page and documentation
- **Static Assets**: CSS and JavaScript files for styling and interactivity
- **Responsive Design**: Mobile-first approach using Bootstrap grid system

## Data Flow

1. **Data Loading**: Application loads RNC data from TXT file on startup
2. **Request Processing**: 
   - Client sends RNC validation request
   - Rate limiting middleware checks request limits
   - Request is logged and processed
   - RNC service performs validation/lookup
   - Response is returned in JSON format

3. **Error Handling**: 
   - Rate limit exceeded returns 429 status
   - Invalid RNC format handled by service layer
   - File loading errors logged and handled gracefully

## External Dependencies

### Python Packages (Production-Ready)
- **Flask**: Web framework and routing
- **pandas**: Data manipulation and CSV processing 
- **gunicorn**: WSGI HTTP server for production
- **werkzeug**: WSGI utilities and proxy handling

### Frontend Libraries (CDN-delivered)
- **Bootstrap 5.3.0**: UI components and responsive grid
- **Font Awesome 6.0.0**: Icon library
- **Prism.js**: Code syntax highlighting for documentation

### Data Sources
- **RNC Data File**: DGII (Dominican Tax Authority) provided TXT file
- **File Location**: `attached_assets/DGII_RNC_1753101730023.TXT`
- **Format**: Pipe-delimited text file with multiple possible encodings
- **Records**: 739,962 RNC entries loaded in memory

## Deployment Strategy

### PostgreSQL Database Architecture
- **Database**: PostgreSQL for scalable data storage and fast queries
- **ORM**: SQLAlchemy for database operations and model management
- **Data Import**: Automated import from DGII CSV/TXT files on startup
- **Performance**: Indexed RNC column for millisecond lookup times
- **Production Ready**: Reliable database with connection pooling and error handling

### Render.com Deployment Configuration
- **Platform**: Render.com cloud platform
- **Plan**: Free tier compatible
- **Build Command**: `pip install flask pandas gunicorn werkzeug flask-sqlalchemy psycopg2-binary`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 main:app`
- **Database**: PostgreSQL database automatically provisioned
- **Auto-Deploy**: Git push triggers automatic redeployment

### Environment Configuration
- **Port**: Dynamic port using `$PORT` environment variable
- **Debug Mode**: Disabled in production (`FLASK_ENV=production`)
- **Logging**: INFO level for production
- **Session Secret**: Auto-generated secure key
- **Proxy Support**: ProxyFix middleware for HTTPS termination

### Performance Optimizations
- **Worker Configuration**: Single worker to conserve memory on free tier
- **Extended Timeout**: 300 seconds for initial database setup and data import
- **Database Indexing**: Optimized RNC column indexing for fast lookups
- **Connection Pooling**: SQLAlchemy connection pooling for efficient database access
- **Cold Start**: 2-5 minutes first deployment (data import), instant subsequent requests

### Deployment Files
- **render.yaml**: Automatic Render deployment configuration
- **Procfile**: Alternative process definition
- **runtime.txt**: Python 3.11 specification
- **DEPLOY_RENDER.md**: Complete deployment guide
- **README.md**: Project documentation and instructions

### Environment Variables
- **PORT**: Server port (auto-configured by Render)
- **DATABASE_URL**: PostgreSQL connection string (auto-configured by Render)
- **SESSION_SECRET**: Flask session encryption key (auto-generated)
- **FLASK_ENV**: Environment mode (production/development)
- **PYTHON_VERSION**: Python runtime version (3.11.0)

## Recent Changes (January 2025)

### Complete Admin Panel & Token System Implementation
- ✓ Created comprehensive admin authentication system with secure login
- ✓ Built complete admin dashboard with real-time statistics
- ✓ Implemented file upload system for DGII data updates
- ✓ Created advanced API token management system with rate limiting
- ✓ Added database models for AdminUser, APIToken, and DataUpdateLog
- ✓ Designed responsive admin interface with Four One branding
- ✓ Enhanced rate limiting: 10 req/min without token, 60+ req/hour with token
- ✓ Added audit logging for all data import operations
- ✓ Integrated Instagram branding (@fouronesolutionssrl) throughout application
- ✓ Created token request system linking to Instagram contact

### Four One Solutions Branding & UI
- ✓ Applied Four One blue color scheme (#405DE6, #3651DB) throughout
- ✓ Integrated company logo from attached assets into all interfaces  
- ✓ Updated main page with professional Four One Solutions branding
- ✓ Added Instagram contact integration for token requests
- ✓ Enhanced homepage with token pricing tiers and usage examples
- ✓ Created professional admin templates with Four One visual identity

### Security & Performance Enhancements
- ✓ Implemented secure password hashing for admin users
- ✓ Added session management for admin authentication
- ✓ Enhanced rate limiting with both IP-based and token-based controls
- ✓ Added token expiration and usage monitoring capabilities
- ✓ Implemented comprehensive error handling and logging
- ✓ Created admin user initialization (default: admin/admin123)

The application now features a complete professional interface with admin management, advanced token system, Four One Solutions branding, and Instagram integration for customer contact. The system handles 169,000+ RNC records with PostgreSQL backend and provides scalable token-based rate limiting.