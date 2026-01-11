#!/usr/bin/env python3
"""
Database Migration Runner
Executes SQL migration files against the database
"""
import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def get_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)


def run_migration(migration_file: Path):
    """Run a single migration file"""
    print(f"\n📄 Running migration: {migration_file.name}")

    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Execute migration
        cursor.execute(sql)
        conn.commit()
        print(f"✅ Migration {migration_file.name} completed successfully")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration {migration_file.name} failed: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def main():
    """Main migration runner"""
    print("=" * 60)
    print("🔄 Database Migration Runner")
    print("=" * 60)

    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment")
        sys.exit(1)

    print(f"📊 Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Unknown'}")

    # Check migrations directory
    if not MIGRATIONS_DIR.exists():
        print(f"❌ Migrations directory not found: {MIGRATIONS_DIR}")
        sys.exit(1)

    # Get all .sql files sorted by name
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    if not migration_files:
        print("⚠️  No migration files found")
        sys.exit(0)

    print(f"\n📂 Found {len(migration_files)} migration(s):")
    for mf in migration_files:
        print(f"   - {mf.name}")

    # Confirm before running
    if len(sys.argv) > 1 and sys.argv[1] == "--yes":
        confirm = "y"
    else:
        confirm = input("\n⚠️  Proceed with migrations? (y/N): ").strip().lower()

    if confirm != "y":
        print("❌ Migration cancelled")
        sys.exit(0)

    # Run migrations
    success_count = 0
    for migration_file in migration_files:
        if run_migration(migration_file):
            success_count += 1
        else:
            print(f"\n❌ Migration failed. Stopping.")
            sys.exit(1)

    print("\n" + "=" * 60)
    print(f"✅ All migrations completed ({success_count}/{len(migration_files)})")
    print("=" * 60)


if __name__ == "__main__":
    main()
