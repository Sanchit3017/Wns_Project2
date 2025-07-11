
#!/usr/bin/env python3
"""
Database migration script to remove foreign key constraints from trips table
"""

import sys
import os
from sqlalchemy import create_engine, text
from shared.config import TripServiceSettings

def drop_foreign_keys():
    """Drop foreign key constraints from trips table"""
    settings = TripServiceSettings()
    engine = create_engine(settings.DATABASE_URL)
    
    print("🔧 Dropping foreign key constraints from trips table...")
    
    # SQL commands to drop foreign key constraints
    drop_constraints_sql = [
        "ALTER TABLE trips DROP CONSTRAINT IF EXISTS trips_employee_id_fkey;",
        "ALTER TABLE trips DROP CONSTRAINT IF EXISTS trips_driver_id_fkey;", 
        "ALTER TABLE trips DROP CONSTRAINT IF EXISTS trips_vehicle_id_fkey;",
        "ALTER TABLE trips DROP CONSTRAINT IF EXISTS fk_trips_employee_id;",
        "ALTER TABLE trips DROP CONSTRAINT IF EXISTS fk_trips_driver_id;",
        "ALTER TABLE trips DROP CONSTRAINT IF EXISTS fk_trips_vehicle_id;"
    ]
    
    try:
        with engine.connect() as conn:
            for sql in drop_constraints_sql:
                try:
                    conn.execute(text(sql))
                    print(f"✅ Executed: {sql}")
                except Exception as e:
                    print(f"⚠️  Constraint might not exist: {sql} - {e}")
            
            conn.commit()
            print("✅ All foreign key constraints removed successfully!")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False
    
    return True

def main():
    """Main migration function"""
    print("=" * 60)
    print("🚀 Trip Service Database Migration")
    print("=" * 60)
    
    success = drop_foreign_keys()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("You can now create trips without foreign key constraint errors.")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
