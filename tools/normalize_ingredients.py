# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "sqlalchemy",
# ]
# ///

import sys
import os
import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path to import models
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(backend_path)

from database import Base
from models import Recipe, Ingredient # Ensure models are loaded

# Database setup (using the same DB as backend)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(backend_path, 'sql_app.db')}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def normalize_ingredients():
    db = SessionLocal()
    try:
        print("Scanning ingredients for country suffixes...")
        ingredients = db.query(Ingredient).all()

        # Regex to match space followed by 2 uppercase letters at the end (e.g., " BE", " FR")
        # You can add more codes or make it stricter if needed
        suffix_pattern = re.compile(r'\s+(BE|FR|NL|DE|IT|ES|UK|US|EU)$')

        count = 0
        for ing in ingredients:
            original_name = ing.name
            match = suffix_pattern.search(original_name)
            if match:
                new_name = suffix_pattern.sub('', original_name)
                if new_name != original_name:
                    print(f"Renaming '{original_name}' -> '{new_name}'")
                    ing.name = new_name
                    count += 1

        if count > 0:
            print(f"Committing {count} changes...")
            db.commit()
            print("Done.")
        else:
            print("No ingredients found needing normalization.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    normalize_ingredients()
