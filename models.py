from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class RNCRecord(db.Model):
    __tablename__ = 'rnc_records'
    
    id = db.Column(db.Integer, primary_key=True)
    rnc = db.Column(db.String(11), unique=True, nullable=False, index=True)
    nombre = db.Column(db.Text)
    estado = db.Column(db.String(50))
    categoria = db.Column(db.String(100))
    actividad_economica = db.Column(db.Text)
    fecha_registro = db.Column(db.String(20))
    regimen = db.Column(db.String(50))
    
    # Additional fields from DGII file
    campo_3 = db.Column(db.Text)  # Unnamed column 2
    campo_4 = db.Column(db.Text)  # Usually activity description
    campo_5 = db.Column(db.Text)  # Additional info
    campo_6 = db.Column(db.Text)  # Additional info
    campo_7 = db.Column(db.Text)  # Additional info
    campo_8 = db.Column(db.Text)  # Additional info
    
    def __repr__(self):
        return f'<RNCRecord {self.rnc}: {self.nombre}>'
    
    def to_dict(self):
        """Convert RNC record to dictionary for API responses"""
        result = {}
        
        # Add main fields if they have values
        if self.nombre and self.nombre.strip():
            result['nombre'] = self.nombre.strip()
        if self.estado and self.estado.strip():
            result['estado'] = self.estado.strip()
        if self.categoria and self.categoria.strip():
            result['categoria'] = self.categoria.strip()
        if self.actividad_economica and self.actividad_economica.strip():
            result['actividad_economica'] = self.actividad_economica.strip()
        if self.fecha_registro and self.fecha_registro.strip():
            result['fecha_registro'] = self.fecha_registro.strip()
        if self.regimen and self.regimen.strip():
            result['regimen'] = self.regimen.strip()
            
        # Add additional fields if they contain meaningful data
        for i, field in enumerate([self.campo_3, self.campo_4, self.campo_5, 
                                 self.campo_6, self.campo_7, self.campo_8], 3):
            if field and field.strip() and field.strip() != '.':
                result[f'campo_{i}'] = field.strip()
        
        return result


class AdminUser(db.Model):
    """Admin user model for data management"""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'


class APIToken(db.Model):
    """API token model for rate limiting and access control"""
    __tablename__ = 'api_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)  # Token description/name
    requests_per_hour = db.Column(db.Integer, default=60)  # Rate limit per hour
    requests_used = db.Column(db.Integer, default=0)
    last_reset = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Optional expiration
    
    # Optional user association
    created_by = db.Column(db.String(100))
    
    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    def reset_if_needed(self):
        """Reset request count if an hour has passed"""
        current_time = datetime.utcnow()
        if self.last_reset is None or current_time - self.last_reset >= timedelta(hours=1):
            import logging
            logging.info(f"Token {self.name}: Resetting request count from {self.requests_used} to 0. Last reset: {self.last_reset}, Current time: {current_time}")
            self.requests_used = 0
            self.last_reset = current_time
            db.session.commit()
    
    def can_make_request(self):
        """Check if token can make another request"""
        self.reset_if_needed()
        return self.is_active and (self.requests_used or 0) < self.requests_per_hour
    
    def use_request(self):
        """Increment request counter"""
        import logging
        old_count = self.requests_used or 0
        self.requests_used = old_count + 1
        logging.info(f"Token {self.name}: Using request #{self.requests_used}/{self.requests_per_hour}")
        db.session.commit()
    
    def is_expired(self):
        """Check if token is expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def __repr__(self):
        return f'<APIToken {self.name}: {self.token[:8]}...>'


class DataUpdateLog(db.Model):
    """Log of data updates for audit trail"""
    __tablename__ = 'data_update_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    records_imported = db.Column(db.Integer, default=0)
    records_updated = db.Column(db.Integer, default=0)
    records_new = db.Column(db.Integer, default=0)
    import_duration = db.Column(db.Float)  # seconds
    admin_user = db.Column(db.String(80))
    status = db.Column(db.String(20), default='success')  # success, error, partial
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DataUpdateLog {self.filename}: {self.records_imported} records>'