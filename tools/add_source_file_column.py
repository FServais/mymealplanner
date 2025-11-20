# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "sqlalchemy",
# ]
# ///

from sqlalchemy import create_engine, text
import os

# Assuming database is at ./sql_app.db or similar, checking main.py or database.py
# database.py usually defines SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# Get absolute path to the database file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "sql_app.db")
DB_URL = f"sqlite:///{DB_PATH}"

def migrate():
    print("Migrating database...")
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(recipes)"))
            columns = [row[1] for row in result]
            if "source_file" in columns:
                print("Column 'source_file' already exists.")
                return

            # Add column
            print("Adding column 'source_file' to 'recipes' table...")
            conn.execute(text("ALTER TABLE recipes ADD COLUMN source_file VARCHAR"))
            print("Migration successful.")
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
