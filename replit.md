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

### Database-Free Architecture
- **No External Database**: All data loaded from CSV/TXT files into memory
- **Fast Lookups**: Pandas DataFrame with indexed RNC column
- **Memory Efficient**: Optimized data loading with proper encoding detection
- **Production Ready**: No database maintenance or connection issues

### Render.com Deployment Configuration
- **Platform**: Render.com cloud platform
- **Plan**: Free tier compatible
- **Build Command**: `pip install flask pandas gunicorn werkzeug`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 60 main:app`
- **Auto-Deploy**: Git push triggers automatic redeployment

### Environment Configuration
- **Port**: Dynamic port using `$PORT` environment variable
- **Debug Mode**: Disabled in production (`FLASK_ENV=production`)
- **Logging**: INFO level for production
- **Session Secret**: Auto-generated secure key
- **Proxy Support**: ProxyFix middleware for HTTPS termination

### Performance Optimizations
- **Worker Configuration**: Single worker to conserve memory on free tier
- **Extended Timeout**: 60 seconds for initial data loading
- **Memory Usage**: ~200MB for 700k+ RNC records
- **Cold Start**: 30-60 seconds first load, instant subsequent requests

### Deployment Files
- **render.yaml**: Automatic Render deployment configuration
- **Procfile**: Alternative process definition
- **runtime.txt**: Python 3.11 specification
- **DEPLOY_RENDER.md**: Complete deployment guide
- **README.md**: Project documentation and instructions

### Environment Variables
- **PORT**: Server port (auto-configured by Render)
- **SESSION_SECRET**: Flask session encryption key (auto-generated)
- **FLASK_ENV**: Environment mode (production/development)
- **PYTHON_VERSION**: Python runtime version (3.11.0)

## Recent Changes (January 2025)

### Database Removal and Render Preparation
- ✓ Removed all database dependencies (SQLAlchemy, PostgreSQL)
- ✓ Configured dynamic port binding for cloud deployment
- ✓ Added production-ready logging configuration
- ✓ Created Render deployment files (render.yaml, Procfile)
- ✓ Optimized data loading performance for production
- ✓ Fixed type safety issues in API routes
- ✓ Added comprehensive deployment documentation
- ✓ Configured gunicorn with production settings

The application is now fully prepared for deployment on Render.com with zero database dependencies and optimized for cloud hosting performance.