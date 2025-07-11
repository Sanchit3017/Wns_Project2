
#!/usr/bin/env python3
"""
Database migration script to remove foreign key constraints from trips table
"""
import os
import sys
from pathlib import Path

# Add shared directory to path
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from shared.config import TripServiceSettings

def migrate_database():
    """Remove foreign key constraints from trips table"""
    settings = TripServiceSettings()
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Start a transaction
            trans = connection.begin()
            
            try:
                # Drop foreign key constraints if they exist
                print("Dropping foreign key constraints...")
                
                # Check if constraints exist and drop them
                constraints_to_drop = [
                    "trips_employee_id_fkey",
                    "trips_driver_id_fkey", 
                    "trips_vehicle_id_fkey"
                ]
                
                for constraint_name in constraints_to_drop:
                    try:
                        connection.execute(text(f"ALTER TABLE trips DROP CONSTRAINT IF EXISTS {constraint_name}"))
                        print(f"✓ Dropped constraint: {constraint_name}")
                    except Exception as e:
                        print(f"Note: Could not drop {constraint_name}: {e}")
                
                # Commit the transaction
                trans.commit()
                print("✅ Database migration completed successfully!")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting database migration...")
    success = migrate_database()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)
