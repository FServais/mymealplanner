# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx",
# ]
# ///

import httpx
import json

API_URL = "http://localhost:8000"

def test_filename_storage():
    print("Testing Filename Storage...")
    
    # 1. Create a recipe with source_file
    recipe_data = {
        "name": "Test Recipe With File",
        "description": "A test recipe",
        "source_file": "test_recipe.pdf",
        "ingredients": [{"name": "Test Ingredient", "quantity": "1"}],
        "instructions": [{"step_number": 1, "text": "Test instruction"}]
    }
    
    try:
        response = httpx.post(f"{API_URL}/recipes/", json=recipe_data)
        response.raise_for_status()
        created_recipe = response.json()
        print(f"Created Recipe ID: {created_recipe['id']}")
        
        # 2. Verify source_file is saved
        if created_recipe.get("source_file") == "test_recipe.pdf":
            print("SUCCESS: source_file was saved correctly.")
        else:
            print(f"FAILURE: source_file mismatch. Expected 'test_recipe.pdf', got '{created_recipe.get('source_file')}'")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_filename_storage()
