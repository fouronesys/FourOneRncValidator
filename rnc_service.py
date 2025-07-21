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
        """Validate RNC format (should be 11 digits)"""
        if not rnc:
            return False
        
        # Remove any spaces or dashes
        clean_rnc = re.sub(r'[^0-9]', '', rnc)
        
        # Dominican RNCs should be 11 digits
        return len(clean_rnc) == 11 and clean_rnc.isdigit()
    
    def search_rnc(self, rnc: str) -> Tuple[bool, Optional[Dict]]:
        """Search for RNC in the database"""
        try:
            # Clean the input RNC
            clean_rnc = re.sub(r'[^0-9]', '', rnc)
            
            # Validate format
            if not self.validate_rnc_format(clean_rnc):
                return False, {"error": "Invalid RNC format. RNC must be 11 digits."}
            
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