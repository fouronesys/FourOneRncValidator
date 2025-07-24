import os
import logging
import time
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from functools import wraps
from models import db, AdminUser, APIToken, DataUpdateLog

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin session management
def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Usuario y contraseña son requeridos', 'error')
            return render_template('admin/login.html')
        
        admin = AdminUser.query.filter_by(username=username, is_active=True).first()
        
        if admin and admin.check_password(password):
            session['admin_logged_in'] = True
            session['admin_username'] = admin.username
            admin.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Credenciales inválidas', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get system statistics
    from rnc_service import rnc_service
    stats = rnc_service.get_database_stats()
    
    # Get recent data updates
    recent_updates = DataUpdateLog.query.order_by(DataUpdateLog.created_at.desc()).limit(10).all()
    
    # Get token statistics
    active_tokens = APIToken.query.filter_by(is_active=True).count()
    total_tokens = APIToken.query.count()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_updates=recent_updates,
                         active_tokens=active_tokens,
                         total_tokens=total_tokens)

@admin_bp.route('/upload-data', methods=['GET', 'POST'])
@admin_required
def upload_data():
    """Upload and process new DGII data file"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        if file and file.filename and allowed_file(file.filename):
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join('attached_assets', filename)
                file.save(filepath)
                
                # Import data using existing importer
                start_time = time.time()
                
                # Log the import attempt
                log_entry = DataUpdateLog()
                log_entry.filename = filename
                log_entry.admin_user = session.get('admin_username')
                log_entry.status = 'processing'
                db.session.add(log_entry)
                db.session.commit()
                
                try:
                    from data_importer import DataImporter
                    importer = DataImporter()
                    result = importer.import_from_file(filepath)
                    import_duration = time.time() - start_time
                    
                    # Update log with results
                    log_entry.records_imported = result.get('total_imported', 0)
                    log_entry.records_updated = result.get('updated', 0)
                    log_entry.records_new = result.get('new', 0)
                    log_entry.import_duration = import_duration
                    log_entry.status = 'success'
                    db.session.commit()
                    
                    flash(f'Datos importados exitosamente: {result.get("total_imported", 0)} registros en {import_duration:.2f} segundos', 'success')
                    logging.info(f'Data import successful by {session.get("admin_username")}: {result}')
                    
                except Exception as import_error:
                    log_entry.status = 'error'
                    log_entry.error_message = str(import_error)
                    db.session.commit()
                    
                    flash(f'Error al importar datos: {str(import_error)}', 'error')
                    logging.error(f'Data import failed: {import_error}')
                
            except Exception as e:
                flash(f'Error al procesar archivo: {str(e)}', 'error')
                logging.error(f'File processing error: {e}')
        else:
            flash('Tipo de archivo no permitido. Use archivos .txt o .csv', 'error')
    
    return render_template('admin/upload_data.html')

@admin_bp.route('/tokens')
@admin_required
def manage_tokens():
    """Manage API tokens"""
    tokens = APIToken.query.order_by(APIToken.created_at.desc()).all()
    return render_template('admin/tokens.html', tokens=tokens)

@admin_bp.route('/tokens/create', methods=['POST'])
@admin_required
def create_token():
    """Create new API token"""
    name = request.form.get('name')
    requests_per_hour = request.form.get('requests_per_hour', 60, type=int)
    expires_days = request.form.get('expires_days', type=int)
    
    if not name:
        flash('El nombre del token es requerido', 'error')
        return redirect(url_for('admin.manage_tokens'))
    
    # Create new token
    token = APIToken()
    token.token = APIToken.generate_token()
    token.name = name
    token.requests_per_hour = requests_per_hour
    token.created_by = session.get('admin_username')
    
    if expires_days:
        from datetime import timedelta
        token.expires_at = datetime.utcnow() + timedelta(days=expires_days)
    
    db.session.add(token)
    db.session.commit()
    
    flash(f'Token creado exitosamente: {token.token}', 'success')
    return redirect(url_for('admin.manage_tokens'))

@admin_bp.route('/tokens/<int:token_id>/toggle')
@admin_required
def toggle_token(token_id):
    """Toggle token active status"""
    token = APIToken.query.get_or_404(token_id)
    token.is_active = not token.is_active
    db.session.commit()
    
    status = 'activado' if token.is_active else 'desactivado'
    flash(f'Token {status} exitosamente', 'success')
    return redirect(url_for('admin.manage_tokens'))

@admin_bp.route('/tokens/<int:token_id>/delete', methods=['POST'])
@admin_required
def delete_token(token_id):
    """Delete API token"""
    token = APIToken.query.get_or_404(token_id)
    db.session.delete(token)
    db.session.commit()
    
    flash('Token eliminado exitosamente', 'success')
    return redirect(url_for('admin.manage_tokens'))

@admin_bp.route('/logs')
@admin_required
def view_logs():
    """View data update logs"""
    page = request.args.get('page', 1, type=int)
    logs = DataUpdateLog.query.order_by(DataUpdateLog.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/logs.html', logs=logs)

@admin_bp.route('/manual-import', methods=['POST'])
@admin_required
def manual_import():
    """Manually reimport all data from the main DGII file"""
    try:
        file_path = "attached_assets/DGII_RNC_1753101730023.TXT"
        
        if not os.path.exists(file_path):
            flash('Archivo DGII no encontrado', 'error')
            return redirect(url_for('admin.dashboard'))
        
        # Log the import attempt
        log_entry = DataUpdateLog()
        log_entry.filename = "DGII_RNC_1753101730023.TXT"
        log_entry.admin_user = session.get('admin_username')
        log_entry.status = 'processing'
        db.session.add(log_entry)
        db.session.commit()
        
        start_time = time.time()
        
        try:
            from data_importer import DataImporter
            importer = DataImporter()
            result = importer.import_from_file(file_path, update_existing=True)
            import_duration = time.time() - start_time
            
            # Update log with results
            log_entry.records_imported = result.get('total_imported', 0)
            log_entry.records_updated = result.get('updated', 0)
            log_entry.records_new = result.get('new', 0)
            log_entry.import_duration = import_duration
            log_entry.status = 'success'
            db.session.commit()
            
            flash(f'Importación manual completada: {result.get("total_imported", 0)} registros procesados, {result.get("new", 0)} nuevos, {result.get("updated", 0)} actualizados en {import_duration:.2f} segundos', 'success')
            logging.info(f'Manual import successful by {session.get("admin_username")}: {result}')
            
        except Exception as import_error:
            log_entry.status = 'error'
            log_entry.error_message = str(import_error)
            db.session.commit()
            
            flash(f'Error en importación manual: {str(import_error)}', 'error')
            logging.error(f'Manual import failed: {import_error}')
            
    except Exception as e:
        flash(f'Error al procesar importación manual: {str(e)}', 'error')
        logging.error(f'Manual import processing error: {e}')
    
    return redirect(url_for('admin.dashboard'))

def allowed_file(filename):
    """Check if uploaded file type is allowed"""
    ALLOWED_EXTENSIONS = {'txt', 'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize default admin user if none exists
def init_admin_user():
    """Create default admin user if none exists"""
    if AdminUser.query.count() == 0:
        admin = AdminUser()
        admin.username = 'admin@fourone.com.do'
        admin.email = 'admin@fouronesolutions.com'
        admin.set_password('PSzorro99**')  # Change this in production!
        db.session.add(admin)
        db.session.commit()
        logging.info('Default admin user created')