import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
from models import db
db.init_app(app)

# Create tables and import data
with app.app_context():
    db.create_all()
    
    # Import RNC data if tables are empty
    from models import RNCRecord
    if RNCRecord.query.count() == 0:
        from data_importer import import_rnc_data
        import_rnc_data()
    
    # Initialize admin user
    from admin_routes import init_admin_user
    init_admin_user()

# Import and register routes
from api_routes import api_bp
from admin_routes import admin_bp

app.register_blueprint(api_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
