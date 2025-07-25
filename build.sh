#!/bin/bash
# Build script for Render deployment
set -o errexit

echo "Installing Python dependencies..."
pip3 install Flask==3.1.1
pip3 install Flask-SQLAlchemy==3.1.1
pip3 install gunicorn==23.0.0
pip3 install pandas==2.3.1
pip3 install Werkzeug==3.1.3
pip3 install psycopg2-binary==2.9.10
pip3 install Flask-Login==0.6.3
pip3 install oauthlib==3.3.1
pip3 install PyJWT==2.10.1
pip3 install SQLAlchemy==2.0.41
pip3 install Flask-Dance==7.1.0

echo "Python dependencies installed successfully!"