import pandas as pd
import os
import logging
from models import db, RNCRecord

def import_rnc_data():
    """Import RNC data from DGII file to PostgreSQL database"""
    try:
        file_path = "attached_assets/DGII_RNC_1753101730023.TXT"
        
        if not os.path.exists(file_path):
            logging.error(f"RNC data file not found at {file_path}")
            return False
        
        logging.info("Starting RNC data import to database...")
        
        # Try different encodings
        encodings = ['latin-1', 'windows-1252', 'iso-8859-1', 'utf-8']
        
        for encoding in encodings:
            try:
                logging.info(f"Trying to load RNC data with encoding: {encoding}")
                
                # Read the file
                df = pd.read_csv(
                    file_path,
                    sep='|',
                    encoding=encoding,
                    dtype=str,
                    na_filter=False,
                    low_memory=False
                )
                
                logging.info(f"Successfully loaded {len(df)} records from file")
                break
                
            except Exception as e:
                logging.warning(f"Failed to load with encoding {encoding}: {str(e)}")
                continue
        else:
            logging.error("Failed to load RNC data with any encoding")
            return False
        
        # Clean column names
        df.columns = [col.strip() for col in df.columns]
        
        # Map columns to our model fields
        # Based on the log output, the first column contains RNC numbers
        rnc_column = df.columns[0]  # First column is RNC
        
        logging.info(f"Using column '{rnc_column}' as RNC identifier")
        logging.info(f"Available columns: {list(df.columns)}")
        
        # Prepare records for bulk insert
        records_to_insert = []
        successful_imports = 0
        
        for index, row in df.iterrows():
            try:
                # Extract RNC (first column)
                rnc = str(row[rnc_column]).strip().replace(' ', '')
                
                # Skip if RNC is not valid (should be 11 digits)
                if not rnc.isdigit() or len(rnc) != 11:
                    continue
                
                # Map other columns
                record_data = {
                    'rnc': rnc,
                    'nombre': str(row[df.columns[1]]).strip() if len(df.columns) > 1 else '',
                    'campo_3': str(row[df.columns[2]]).strip() if len(df.columns) > 2 else '',
                    'actividad_economica': str(row[df.columns[3]]).strip() if len(df.columns) > 3 else '',
                    'campo_5': str(row[df.columns[4]]).strip() if len(df.columns) > 4 else '',
                    'campo_6': str(row[df.columns[5]]).strip() if len(df.columns) > 5 else '',
                    'campo_7': str(row[df.columns[6]]).strip() if len(df.columns) > 6 else '',
                    'campo_8': str(row[df.columns[7]]).strip() if len(df.columns) > 7 else '',
                    'fecha_registro': str(row[df.columns[8]]).strip() if len(df.columns) > 8 else '',
                    'estado': str(row[df.columns[9]]).strip() if len(df.columns) > 9 else '',
                    'regimen': str(row[df.columns[10]]).strip() if len(df.columns) > 10 else ''
                }
                
                # Clean empty fields
                for key, value in record_data.items():
                    if value in ['', 'nan', 'None', '.']:
                        record_data[key] = ''
                
                records_to_insert.append(record_data)
                successful_imports += 1
                
                # Batch insert every 1000 records
                if len(records_to_insert) >= 1000:
                    try:
                        for record in records_to_insert:
                            rnc_record = RNCRecord(**record)
                            db.session.add(rnc_record)
                        db.session.commit()
                        logging.info(f"Imported {successful_imports} records so far...")
                        records_to_insert = []
                    except Exception as e:
                        logging.error(f"Error inserting batch: {str(e)}")
                        db.session.rollback()
                        records_to_insert = []
                        
            except Exception as e:
                logging.warning(f"Error processing row {index}: {str(e)}")
                continue
        
        # Insert remaining records
        if records_to_insert:
            try:
                for record in records_to_insert:
                    rnc_record = RNCRecord(**record)
                    db.session.add(rnc_record)
                db.session.commit()
            except Exception as e:
                logging.error(f"Error inserting final batch: {str(e)}")
                db.session.rollback()
        
        logging.info(f"Successfully imported {successful_imports} RNC records to database")
        return True
        
    except Exception as e:
        logging.error(f"Error importing RNC data: {str(e)}")
        db.session.rollback()
        return False