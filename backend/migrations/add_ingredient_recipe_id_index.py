"""
Migration script to add index on ingredients.recipe_id

This index is critical for performance when filtering recipes by ingredients.
Without it, every ingredient-based query requires a full table scan.

Usage:
    python migrations/add_ingredient_recipe_id_index.py
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import database config
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import SQLALCHEMY_DATABASE_URL


def run_migration():
    # Extract database path from SQLAlchemy URL
    # Format: sqlite:///./sql_app.db
    db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if index already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='ix_ingredients_recipe_id'
        """)
        
        if cursor.fetchone():
            print("✓ Index 'ix_ingredients_recipe_id' already exists. No action needed.")
            return
        
        # Create the index
        print("Creating index on ingredients.recipe_id...")
        cursor.execute("""
            CREATE INDEX ix_ingredients_recipe_id ON ingredients (recipe_id)
        """)
        
        conn.commit()
        print("✓ Successfully created index 'ix_ingredients_recipe_id'")
        
        # Verify the index was created
        cursor.execute("""
            SELECT name, sql FROM sqlite_master 
            WHERE type='index' AND name='ix_ingredients_recipe_id'
        """)
        result = cursor.fetchone()
        if result:
            print(f"✓ Verification: {result[0]}")
            print(f"  SQL: {result[1]}")
        
    except sqlite3.Error as e:
        print(f"✗ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add index on ingredients.recipe_id")
    print("=" * 60)
    run_migration()
    print("=" * 60)
    print("Migration complete!")
