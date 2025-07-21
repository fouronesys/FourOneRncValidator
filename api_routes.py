import logging
import time
from flask import Blueprint, request, jsonify, render_template, current_app
from functools import wraps
from collections import defaultdict
from rnc_service import rnc_service

api_bp = Blueprint('api', __name__)

# Simple rate limiting storage (in production, use Redis or similar)
request_counts = defaultdict(list)
RATE_LIMIT_PER_MINUTE = 60

def rate_limit(max_requests=RATE_LIMIT_PER_MINUTE):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            current_time = time.time()
            
            # Clean old requests (older than 1 minute)
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip] 
                if current_time - req_time < 60
            ]
            
            # Check if rate limit exceeded
            if len(request_counts[client_ip]) >= max_requests:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {max_requests} requests per minute allowed"
                }), 429
            
            # Add current request
            request_counts[client_ip].append(current_time)
            
            # Log the request
            logging.info(f"API Request from {client_ip}: {request.method} {request.path}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@api_bp.route('/')
def index():
    """Main page with API documentation"""
    return render_template('index.html')

@api_bp.route('/docs')
def documentation():
    """Detailed API documentation page"""
    stats = rnc_service.get_database_stats()
    return render_template('documentation.html', stats=stats)

@api_bp.route('/api/validate/<rnc>', methods=['GET'])
@rate_limit()
def validate_rnc(rnc):
    """Validate if an RNC exists in the database"""
    try:
        exists, result = rnc_service.search_rnc(rnc)
        
        if exists:
            return jsonify({
                "status": "success",
                "rnc": result["rnc"],
                "exists": True,
                "message": "RNC found in database"
            })
        else:
            return jsonify({
                "status": "error" if "error" in result else "not_found",
                "rnc": result.get("rnc", rnc),
                "exists": False,
                "message": result.get("message", result.get("error", "RNC not found"))
            }), 404 if "error" not in result else 400
            
    except Exception as e:
        logging.error(f"Error validating RNC {rnc}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@api_bp.route('/api/info/<rnc>', methods=['GET'])
@rate_limit()
def get_rnc_info(rnc):
    """Get complete information for an RNC"""
    try:
        exists, result = rnc_service.search_rnc(rnc)
        
        if exists:
            return jsonify({
                "status": "success",
                "rnc": result["rnc"],
                "exists": True,
                "data": result["data"]
            })
        else:
            return jsonify({
                "status": "error" if "error" in result else "not_found",
                "rnc": result.get("rnc", rnc),
                "exists": False,
                "message": result.get("message", result.get("error", "RNC not found"))
            }), 404 if "error" not in result else 400
            
    except Exception as e:
        logging.error(f"Error getting RNC info {rnc}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@api_bp.route('/api/status', methods=['GET'])
def api_status():
    """Get API and database status"""
    stats = rnc_service.get_database_stats()
    
    return jsonify({
        "status": "online",
        "database": stats,
        "api_version": "1.0.0",
        "brand": "Four One RNC Validator"
    })

@api_bp.route('/api/search', methods=['POST'])
@rate_limit(30)  # Lower rate limit for search endpoint
def search_rncs():
    """Batch search for multiple RNCs"""
    try:
        data = request.get_json()
        
        if not data or 'rncs' not in data:
            return jsonify({
                "status": "error",
                "message": "Request body must contain 'rncs' array"
            }), 400
        
        rncs = data['rncs']
        
        if not isinstance(rncs, list):
            return jsonify({
                "status": "error",
                "message": "'rncs' must be an array"
            }), 400
        
        if len(rncs) > 10:  # Limit batch size
            return jsonify({
                "status": "error",
                "message": "Maximum 10 RNCs per batch request"
            }), 400
        
        results = []
        for rnc in rncs:
            exists, result = rnc_service.search_rnc(str(rnc))
            
            if exists:
                results.append({
                    "rnc": result["rnc"],
                    "exists": True,
                    "data": result["data"]
                })
            else:
                results.append({
                    "rnc": result.get("rnc", rnc),
                    "exists": False,
                    "message": result.get("message", result.get("error", "RNC not found"))
                })
        
        return jsonify({
            "status": "success",
            "results": results,
            "total": len(results)
        })
        
    except Exception as e:
        logging.error(f"Error in batch search: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404

@api_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle method not allowed errors"""
    return jsonify({
        "status": "error",
        "message": "Method not allowed"
    }), 405
