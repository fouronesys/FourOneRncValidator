import pandas as pd
import os
import logging
from models import db, RNCRecord, DataUpdateLog
from datetime import datetime

class DataImporter:
    """Enhanced data importer with update/insert capabilities and progress tracking"""
    
    def __init__(self):
        self.batch_size = 10000  # Increased batch size for better performance
        self.supported_encodings = ['latin-1', 'windows-1252', 'iso-8859-1', 'utf-8']
    
    def import_from_file(self, file_path: str, update_existing: bool = True) -> dict:
        """Import data from file with optional updates"""
        stats = {
            'total_processed': 0,
            'total_imported': 0,
            'new': 0,
            'updated': 0,
            'errors': 0
        }
        
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            logging.info(f"Starting data import from: {file_path}")
            
            # Load data with encoding detection
            df = self._load_file_with_encoding(file_path)
            if df is None:
                raise Exception("Failed to load file with any supported encoding")
            
            stats['total_processed'] = len(df)
            logging.info(f"Processing {len(df)} records")
            
            # Process in batches
            return self._process_dataframe(df, update_existing, stats)
            
        except Exception as e:
            logging.error(f"Import error: {str(e)}")
            stats['errors'] += 1
            return stats
    
    def _load_file_with_encoding(self, file_path: str):
        """Try loading file with different encodings"""
        for encoding in self.supported_encodings:
            try:
                logging.info(f"Trying encoding: {encoding}")
                df = pd.read_csv(
                    file_path,
                    sep='|',
                    encoding=encoding,
                    dtype=str,
                    na_filter=False,
                    low_memory=False
                )
                logging.info(f"Successfully loaded with {encoding}")
                return df
            except Exception as e:
                logging.warning(f"Failed with {encoding}: {str(e)}")
                continue
        return None
    
    def _process_dataframe(self, df, update_existing, stats):
        """Process dataframe in batches with progress tracking"""
        df.columns = [col.strip() for col in df.columns]
        rnc_column = df.columns[0]
        
        total_rows = len(df)
        processed_rows = 0
        records_to_insert = []
        
        # Progress tracking
        progress_interval = max(1000, total_rows // 100)  # Show progress every 1000 or 1% of records
        
        logging.info(f"📊 Starting import of {total_rows:,} records...")
        logging.info("🚀 Progress: [          ] 0%")
        
        for index, row in df.iterrows():
            try:
                # Extract and validate RNC
                rnc = str(row[rnc_column]).strip().replace(' ', '')
                if not rnc.isdigit() or len(rnc) not in [9, 11]:
                    continue
                
                # Prepare record data
                record_data = self._prepare_record_data(row, df.columns, rnc)
                records_to_insert.append(record_data)
                stats['new'] += 1
                processed_rows += 1
                
                # Process batch when full
                if len(records_to_insert) >= self.batch_size:
                    self._process_batch_fast(records_to_insert, stats)
                    records_to_insert = []
                
                # Show progress
                if processed_rows % progress_interval == 0 or processed_rows == total_rows:
                    self._show_progress(processed_rows, total_rows)
                    
            except Exception as e:
                stats['errors'] += 1
                logging.warning(f"❌ Error processing row {index}: {str(e)}")
        
        # Process remaining records
        if records_to_insert:
            self._process_batch_fast(records_to_insert, stats)
        
        logging.info(f"✅ Import completed successfully!")
        logging.info(f"📈 Final stats: {stats}")
        return stats
    
    def _show_progress(self, current, total):
        """Display progress bar in logs"""
        percentage = (current / total) * 100
        filled = int(percentage // 10)
        bar = "█" * filled + "░" * (10 - filled)
        logging.info(f"🚀 Progress: [{bar}] {percentage:.1f}% ({current:,}/{total:,})")
    
    def _process_batch_fast(self, records, stats):
        """Fast batch processing using bulk insert"""
        if not records:
            return
            
        try:
            # Use bulk insert for better performance
            db.session.bulk_insert_mappings(RNCRecord, records)
            db.session.commit()
            stats['total_imported'] += len(records)
            logging.info(f"✅ Imported batch of {len(records):,} records")
            
        except Exception as e:
            logging.warning(f"⚠️ Bulk insert failed, trying individual inserts: {str(e)}")
            db.session.rollback()
            
            # Fallback: individual inserts
            for record in records:
                try:
                    new_record = RNCRecord(**record)
                    db.session.add(new_record)
                    db.session.commit()
                    stats['total_imported'] += 1
                except Exception as individual_error:
                    db.session.rollback()
                    stats['errors'] += 1
                    logging.debug(f"❌ Failed to insert RNC {record.get('rnc', 'unknown')}: {str(individual_error)}")
    
    def _prepare_record_data(self, row, columns, rnc):
        """Prepare record data from row"""
        record_data = {
            'rnc': rnc,
            'nombre': str(row[columns[1]]).strip() if len(columns) > 1 else '',
            'campo_3': str(row[columns[2]]).strip() if len(columns) > 2 else '',
            'actividad_economica': str(row[columns[3]]).strip() if len(columns) > 3 else '',
            'campo_5': str(row[columns[4]]).strip() if len(columns) > 4 else '',
            'campo_6': str(row[columns[5]]).strip() if len(columns) > 5 else '',
            'campo_7': str(row[columns[6]]).strip() if len(columns) > 6 else '',
            'campo_8': str(row[columns[7]]).strip() if len(columns) > 7 else '',
            'fecha_registro': str(row[columns[8]]).strip() if len(columns) > 8 else '',
            'estado': str(row[columns[9]]).strip() if len(columns) > 9 else '',
            'regimen': str(row[columns[10]]).strip() if len(columns) > 10 else ''
        }
        
        # Clean empty/invalid values
        for key, value in record_data.items():
            if value in ['', 'nan', 'None', '.', 'NaN']:
                record_data[key] = ''
        
        return record_data
    
    def _process_batch_legacy(self, insert_records, update_records, stats):
        """Legacy batch processing (kept for compatibility)"""
        try:
            # Insert new records using individual inserts to avoid mapper issues
            if insert_records:
                try:
                    for record in insert_records:
                        rnc_record = RNCRecord(**record)
                        db.session.add(rnc_record)
                    db.session.commit()
                    stats['total_imported'] += len(insert_records)
                    logging.info(f"Inserted {len(insert_records)} new records")
                except Exception as e:
                    db.session.rollback()
                    # Try one by one
                    for record in insert_records:
                        try:
                            existing = RNCRecord.query.filter_by(rnc=record['rnc']).first()
                            if not existing:
                                rnc_record = RNCRecord(**record)
                                db.session.add(rnc_record)
                                db.session.commit()
                                stats['total_imported'] += 1
                        except Exception:
                            db.session.rollback()
                            stats['errors'] += 1
            
            # Update existing records
            if update_records:
                for existing_record, new_data in update_records:
                    for key, value in new_data.items():
                        if key != 'rnc':  # Don't update the primary key
                            setattr(existing_record, key, value)
                stats['updated'] += len(update_records)
                stats['total_imported'] += len(update_records)
                db.session.commit()
                logging.info(f"Updated {len(update_records)} existing records")
            
            logging.info(f"Batch processed: +{len(insert_records)} new, ~{len(update_records)} updated")
            
        except Exception as e:
            logging.error(f"Batch processing error: {str(e)}")
            db.session.rollback()
            stats['errors'] += len(insert_records) + len(update_records)

def import_rnc_data():
    """Legacy import function for initial setup"""
    importer = DataImporter()
    file_path = "attached_assets/DGII_RNC_1753101730023.TXT"
    
    # Use the enhanced importer for initial setup
    result = importer.import_from_file(file_path, update_existing=False)
    
    if result.get('total_imported', 0) > 0:
        logging.info(f"Initial import completed: {result['total_imported']} records imported")
        return True
    else:
        logging.error(f"Initial import failed: {result}")
        return False