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

### Python Packages
- **Flask**: Web framework and routing
- **pandas**: Data manipulation and CSV processing
- **werkzeug**: WSGI utilities and proxy handling

### Frontend Libraries (CDN-delivered)
- **Bootstrap 5.3.0**: UI components and responsive grid
- **Font Awesome 6.0.0**: Icon library
- **Prism.js**: Code syntax highlighting for documentation

### Data Sources
- **RNC Data File**: DGII (Dominican Tax Authority) provided TXT file
- **File Location**: `attached_assets/DGII_RNC_1753101730023.TXT`
- **Format**: Pipe-delimited text file with multiple possible encodings

## Deployment Strategy

### Development Configuration
- **Host**: 0.0.0.0 (accepts connections from any IP)
- **Port**: 5000
- **Debug Mode**: Enabled for development
- **Session Secret**: Environment variable with fallback

### Production Considerations
- **Proxy Support**: ProxyFix middleware configured for reverse proxy deployment
- **Logging**: Configurable logging level (currently DEBUG)
- **Rate Limiting**: In-memory storage should be replaced with Redis/Memcached
- **Security**: Session secret should be set via environment variable

### Environment Variables
- **SESSION_SECRET**: Flask session encryption key
- **Additional configuration can be added as needed**

The application is designed for easy deployment on platforms like Replit, with support for both development and production environments through environment-based configuration.