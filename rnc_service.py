import pandas as pd
import os
import re
import logging
from typing import Dict, List, Optional, Tuple

class RNCService:
    def __init__(self):
        self.rnc_data = None
        self.data_loaded = False
        self.load_rnc_data()
    
    def load_rnc_data(self):
        """Load RNC data from the uploaded file with proper encoding handling"""
        try:
            # Try to find the RNC file in attached_assets directory
            file_path = "attached_assets/DGII_RNC_1753101730023.TXT"
            
            if not os.path.exists(file_path):
                logging.error(f"RNC data file not found at {file_path}")
                return
            
            # Try different encodings commonly used in Dominican Republic
            encodings = ['latin-1', 'windows-1252', 'iso-8859-1', 'utf-8']
            
            for encoding in encodings:
                try:
                    logging.info(f"Trying to load RNC data with encoding: {encoding}")
                    
                    # Read the file with the current encoding
                    self.rnc_data = pd.read_csv(
                        file_path,
                        sep='|',  # Common separator for DGII files
                        encoding=encoding,
                        dtype=str,  # Keep all data as strings to preserve RNC format
                        na_filter=False  # Don't convert empty strings to NaN
                    )
                    
                    logging.info(f"Successfully loaded RNC data with encoding: {encoding}")
                    logging.info(f"Loaded {len(self.rnc_data)} RNC records")
                    logging.info(f"Columns: {list(self.rnc_data.columns)}")
                    
                    # Clean column names (remove extra spaces)
                    self.rnc_data.columns = [col.strip() for col in self.rnc_data.columns]
                    
                    # Try to identify the RNC column (usually the first one or named RNC/CEDULA)
                    possible_rnc_columns = ['RNC', 'CEDULA', 'NUMERO', 'ID']
                    rnc_column = None
                    
                    for col in possible_rnc_columns:
                        if col in self.rnc_data.columns:
                            rnc_column = col
                            break
                    
                    if rnc_column is None and len(self.rnc_data.columns) > 0:
                        rnc_column = self.rnc_data.columns[0]  # Use first column as RNC
                    
                    if rnc_column:
                        # Clean RNC data - remove spaces and ensure proper format
                        self.rnc_data[rnc_column] = self.rnc_data[rnc_column].astype(str).str.replace(' ', '').str.strip()
                        
                        # Create an index for faster lookups
                        self.rnc_data.set_index(rnc_column, inplace=True)
                        logging.info(f"Using column '{rnc_column}' as RNC identifier")
                    
                    self.data_loaded = True
                    break
                    
                except Exception as e:
                    logging.warning(f"Failed to load with encoding {encoding}: {str(e)}")
                    continue
            
            if not self.data_loaded:
                logging.error("Failed to load RNC data with any supported encoding")
                
        except Exception as e:
            logging.error(f"Error loading RNC data: {str(e)}")
    
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
        if not self.data_loaded or self.rnc_data is None:
            return False, {"error": "RNC database not available"}
        
        # Clean the input RNC
        clean_rnc = re.sub(r'[^0-9]', '', rnc)
        
        # Validate format
        if not self.validate_rnc_format(clean_rnc):
            return False, {"error": "Invalid RNC format. RNC must be 11 digits."}
        
        try:
            # Search in the index
            if clean_rnc in self.rnc_data.index:
                record = self.rnc_data.loc[clean_rnc]
                
                # Convert to dict and clean up the data
                if isinstance(record, pd.Series):
                    result = record.to_dict()
                else:
                    # If multiple records, take the first one
                    result = record.iloc[0].to_dict() if len(record) > 0 else {}
                
                # Clean up the result
                cleaned_result = {}
                for key, value in result.items():
                    if pd.notna(value) and str(value).strip():
                        cleaned_result[key.strip()] = str(value).strip()
                
                return True, {
                    "rnc": clean_rnc,
                    "exists": True,
                    "data": cleaned_result
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
        """Get statistics about the loaded database"""
        if not self.data_loaded or self.rnc_data is None:
            return {"loaded": False, "error": "Database not loaded"}
        
        return {
            "loaded": True,
            "total_records": len(self.rnc_data),
            "columns": list(self.rnc_data.columns),
            "sample_rnc": self.rnc_data.index[0] if len(self.rnc_data) > 0 else None
        }

# Global service instance
rnc_service = RNCService()
