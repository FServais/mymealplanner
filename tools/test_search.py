# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx",
# ]
# ///

import httpx
import sys

API_URL = "http://localhost:8000"

def test_search():
    print("Testing Recipe Search...")
    
    # 1. Search for a known recipe
    # Assuming we have "Sauté" from previous output
    query = "Sauté"
    print(f"Searching for '{query}'...")
    try:
        response = httpx.get(f"{API_URL}/recipes/", params={"search": query})
        response.raise_for_status()
        recipes = response.json()
        print(f"Found {len(recipes)} recipes:")
        for r in recipes:
            print(f"  - {r['name']}")
            if query.lower() not in r['name'].lower():
                print(f"    ERROR: Recipe {r['name']} does not match search '{query}'!")
    except Exception as e:
        print(f"Error searching recipes: {e}")

    # 2. Search for something that shouldn't exist
    query = "XyZ123"
    print(f"Searching for '{query}'...")
    try:
        response = httpx.get(f"{API_URL}/recipes/", params={"search": query})
        response.raise_for_status()
        recipes = response.json()
        print(f"Found {len(recipes)} recipes (expected 0).")
        if len(recipes) > 0:
            print("    ERROR: Found recipes for non-existent query!")
    except Exception as e:
        print(f"Error searching recipes: {e}")

if __name__ == "__main__":
    test_search()
