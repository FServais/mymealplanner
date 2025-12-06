import sqlite3
import os

DB_PATH = "sql_app.db"

def migrate():
    print("Checking database schema...")
    if not os.path.exists(DB_PATH):
        print("Database not found to migrate.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(tags)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "color" not in columns:
        print("Adding 'color' column to 'tags' table...")
        try:
            cursor.execute("ALTER TABLE tags ADD COLUMN color VARCHAR DEFAULT '#6366f1'")
            conn.commit()
            print("Migration successful.")
        except Exception as e:
            print(f"Migration failed: {e}")
    else:
        print("'color' column already exists.")
        
    conn.close()

if __name__ == "__main__":
    migrate()
