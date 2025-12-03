# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx",
# ]
# ///

import httpx
import json

API_URL = "http://localhost:8000"

def test_filter():
    print("Testing source_file filter...")

    # 1. Create a recipe with a unique source_file
    unique_file = "unique_test_file_v999.pdf"
    recipe_data = {
        "name": "Filter Test Recipe",
        "source_file": unique_file,
        "ingredients": [],
        "instructions": []
    }

    try:
        # Create
        response = httpx.post(f"{API_URL}/recipes/", json=recipe_data)
        response.raise_for_status()
        print("Created test recipe.")

        # 2. Filter by it
        response = httpx.get(f"{API_URL}/recipes/", params={"source_file": unique_file})
        response.raise_for_status()
        results = response.json()

        if len(results) == 1 and results[0]["source_file"] == unique_file:
            print("SUCCESS: Filter returned correct recipe.")
        else:
            print(f"FAILURE: Filter returned {len(results)} results.")

        # 3. Filter by non-existent
        response = httpx.get(f"{API_URL}/recipes/", params={"source_file": "non_existent.pdf"})
        results = response.json()
        if len(results) == 0:
            print("SUCCESS: Filter returned 0 results for non-existent file.")
        else:
            print(f"FAILURE: Filter returned {len(results)} results for non-existent file.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_filter()
