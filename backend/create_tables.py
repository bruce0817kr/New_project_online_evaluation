#!/usr/bin/env python3
"""
Database Table Creation Script
Creates all tables defined in SQLAlchemy models
"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine, Base
from app.models import (
    Project,
    Company,
    Evaluation,
    AuditLog,
    User,
    ScoringTemplate,
    ScoreHistory
)

def create_tables():
    """Create all database tables"""
    print("=" * 60)
    print("🔄 Creating Database Tables")
    print("=" * 60)

    try:
        # Import all models to ensure they're registered
        print("\n📦 Models loaded:")
        print("   - User")
        print("   - Project")
        print("   - Company")
        print("   - Evaluation")
        print("   - AuditLog")
        print("   - ScoringTemplate (NEW)")
        print("   - ScoreHistory (NEW)")

        # Create all tables
        print("\n🔨 Creating tables...")
        Base.metadata.create_all(bind=engine)

        print("\n✅ All tables created successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
