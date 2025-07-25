import logging
import time
from flask import Blueprint, request, jsonify, render_template, current_app
from functools import wraps
from collections import defaultdict
from rnc_service import rnc_service
from models import APIToken, db

api_bp = Blueprint('api', __name__)

# Fallback rate limiting storage for requests without tokens
request_counts = defaultdict(list)
RATE_LIMIT_PER_MINUTE = 10  # Reduced for non-token requests

def token_or_rate_limit(f):
    """Enhanced rate limiting with token support"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        # Check for API token in headers or query params
        token_value = request.headers.get('Authorization', '').replace('Bearer ', '') or request.args.get('token')
        
        if token_value:
            # Token-based rate limiting
            token = APIToken.query.filter_by(token=token_value, is_active=True).first()
            
            if not token:
                return jsonify({
                    "error": "Invalid token",
                    "message": "The provided API token is invalid or inactive"
                }), 401
            
            if token.is_expired():
                return jsonify({
                    "error": "Token expired",
                    "message": "The provided API token has expired"
                }), 401
            
            if not token.can_make_request():
                return jsonify({
                    "error": "Rate limit exceeded",
                    "message": f"Token rate limit exceeded. Maximum {token.requests_per_hour} requests per hour allowed"
                }), 429
            
            # Use the request
            token.use_request()
            logging.info(f"API Request from {client_ip} with token {token.name}: {request.method} {request.path}")
            
        else:
            # IP-based rate limiting for requests without tokens
            current_time = time.time()
            
            # Clean old requests (older than 1 minute)
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip] 
                if current_time - req_time < 60
            ]
            
            # Check if rate limit exceeded
            if len(request_counts[client_ip]) >= RATE_LIMIT_PER_MINUTE:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {RATE_LIMIT_PER_MINUTE} requests per minute allowed without token. Use an API token for higher limits."
                }), 429
            
            # Add current request
            request_counts[client_ip].append(current_time)
            logging.info(f"API Request from {client_ip} (no token): {request.method} {request.path}")
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=RATE_LIMIT_PER_MINUTE):
    """Legacy rate limiting decorator for backward compatibility"""
    return token_or_rate_limit

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
        
        if exists and result:
            return jsonify({
                "status": "success",
                "rnc": result["rnc"],
                "exists": True,
                "message": "RNC found in database"
            })
        else:
            result = result or {}
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
        
        if exists and result:
            return jsonify({
                "status": "success",
                "rnc": result["rnc"],
                "exists": True,
                "data": result["data"]
            })
        else:
            result = result or {}
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
            
            if exists and result:
                results.append({
                    "rnc": result["rnc"],
                    "exists": True,
                    "data": result["data"]
                })
            else:
                result = result or {}
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

@api_bp.route('/api/search-by-name', methods=['GET'])
@rate_limit(30)  # Lower rate limit for search endpoint
def search_by_name():
    """Search companies by name with autocomplete suggestions"""
    try:
        name_query = request.args.get('q') or request.args.get('query')
        limit = request.args.get('limit', 10, type=int)
        
        if not name_query:
            return jsonify({
                "status": "error",
                "message": "Query parameter 'q' or 'query' is required"
            }), 400
        
        # Validate limit
        if limit < 1 or limit > 50:
            limit = 10
        
        success, result = rnc_service.search_by_name(name_query, limit)
        
        if success:
            return jsonify({
                "status": "success",
                "query": result["query"],
                "suggestions": result["suggestions"],
                "total_found": result["total_found"],
                "message": result["message"]
            })
        else:
            return jsonify({
                "status": "not_found" if "No companies found" in result.get("message", "") else "error",
                "query": result.get("query", name_query),
                "suggestions": result.get("suggestions", []),
                "total_found": result.get("total_found", 0),
                "message": result.get("message", result.get("error", "Search failed"))
            }), 404 if "No companies found" in result.get("message", "") else 400
            
    except Exception as e:
        logging.error(f"Error in name search: {str(e)}")
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
