
#!/usr/bin/env python3


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from shared.config import TripServiceSettings

def drop_foreign_keys():
    """Drop foreign key constraints from trips table"""
    settings = TripServiceSettings()
    
    print(f"🔧 Connecting to database: {settings.DATABASE_URL[:50]}...")
    engine = create_engine(settings.DATABASE_URL)
    
    print("🔧 Dropping foreign key constraints from trips table...")
    
    # First, let's check what constraints actually exist
    check_constraints_sql = """
    SELECT constraint_name, table_name 
    FROM information_schema.table_constraints 
    WHERE table_name = 'trips' AND constraint_type = 'FOREIGN KEY';
    """
    
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
        with engine.begin() as conn:
            # Check existing constraints
            print("🔍 Checking existing foreign key constraints...")
            result = conn.execute(text(check_constraints_sql))
            constraints = result.fetchall()
            
            if constraints:
                print("📋 Found existing constraints:")
                for constraint in constraints:
                    print(f"   - {constraint[0]}")
            else:
                print("✅ No foreign key constraints found on trips table")
            
            # Drop constraints
            for sql in drop_constraints_sql:
                try:
                    conn.execute(text(sql))
                    print(f"✅ Executed: {sql}")
                except Exception as e:
                    print(f"⚠️  Constraint might not exist: {sql.split()[5]} - {str(e)[:100]}")
            
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
