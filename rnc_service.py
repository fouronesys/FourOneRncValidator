import re
import logging
from typing import Dict, Optional, Tuple
from models import RNCRecord

class RNCService:
    def __init__(self):
        """Initialize RNC service with database backend"""
        self.data_loaded = True  # Always true since we use database
        logging.info("RNC Service initialized with PostgreSQL backend")
    
    def validate_rnc_format(self, rnc: str) -> bool:
        """Validate RNC format (can be 9 or 11 digits)"""
        if not rnc:
            return False
        
        # Remove any spaces or dashes
        clean_rnc = re.sub(r'[^0-9]', '', rnc)
        
        # Dominican RNCs can be 9 or 11 digits
        return clean_rnc.isdigit() and len(clean_rnc) in [9, 11]
    
    def search_rnc(self, rnc: str) -> Tuple[bool, Optional[Dict]]:
        """Search for RNC in the database"""
        clean_rnc = ""
        try:
            # Clean the input RNC
            clean_rnc = re.sub(r'[^0-9]', '', rnc)
            
            # Validate format
            if not self.validate_rnc_format(clean_rnc):
                return False, {"error": "Invalid RNC format. RNC must be 9 or 11 digits."}
            
            # Search in database
            record = RNCRecord.query.filter_by(rnc=clean_rnc).first()
            
            if record:
                return True, {
                    "rnc": clean_rnc,
                    "exists": True,
                    "data": record.to_dict()
                }
            else:
                return False, {
                    "rnc": clean_rnc,
                    "exists": False,
                    "message": "RNC not found in database"
                }
                
        except Exception as e:
            logging.error(f"Error searching RNC {clean_rnc}: {str(e)}")
            return False, {"error": f"Database search error: {str(e)}"}
    
    def search_by_name(self, name_query: str, limit: int = 10) -> Tuple[bool, Dict]:
        """Search for companies by name with suggestions"""
        try:
            if not name_query or len(name_query.strip()) < 2:
                return False, {"error": "Name query must be at least 2 characters long"}
            
            # Clean and prepare search query
            clean_query = name_query.strip().upper()
            
            # Search using ILIKE for case-insensitive partial matching
            records = RNCRecord.query.filter(
                RNCRecord.nombre.ilike(f'%{clean_query}%')
            ).filter(
                RNCRecord.nombre.isnot(None)
            ).limit(limit).all()
            
            if records:
                suggestions = []
                for record in records:
                    suggestion = {
                        "rnc": record.rnc,
                        "nombre": record.nombre.strip() if record.nombre else "",
                        "estado": record.estado.strip() if record.estado else "",
                    }
                    # Add additional info if available
                    if record.actividad_economica and record.actividad_economica.strip():
                        suggestion["actividad_economica"] = record.actividad_economica.strip()
                    suggestions.append(suggestion)
                
                return True, {
                    "query": name_query,
                    "suggestions": suggestions,
                    "total_found": len(suggestions),
                    "message": f"Found {len(suggestions)} companies matching '{name_query}'"
                }
            else:
                return False, {
                    "query": name_query,
                    "suggestions": [],
                    "total_found": 0,
                    "message": f"No companies found matching '{name_query}'"
                }
                
        except Exception as e:
            logging.error(f"Error searching by name '{name_query}': {str(e)}")
            return False, {"error": f"Database search error: {str(e)}"}

    def get_database_stats(self) -> Dict:
        """Get statistics about the database"""
        try:
            total_records = RNCRecord.query.count()
            
            # Get a sample RNC for demonstration
            sample_record = RNCRecord.query.first()
            sample_rnc = sample_record.rnc if sample_record else None
            
            return {
                "loaded": True,
                "total_records": total_records,
                "columns": ["rnc", "nombre", "estado", "actividad_economica", "fecha_registro", "regimen"],
                "sample_rnc": sample_rnc
            }
        except Exception as e:
            logging.error(f"Error getting database stats: {str(e)}")
            return {"loaded": False, "error": str(e)}

# Global service instance
rnc_service = RNCService()