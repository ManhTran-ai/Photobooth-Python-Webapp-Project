#!/usr/bin/env python3
"""Reset database script"""

from app import create_app
from models.database import db

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        try:
            # Drop all tables
            db.drop_all()
            print("Dropped all tables")

            # Create all tables
            db.create_all()
            print("Created all tables")

            print("Database reset successfully!")

        except Exception as e:
            print(f"Error resetting database: {e}")
            import traceback
            traceback.print_exc()