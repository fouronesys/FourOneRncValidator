from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

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