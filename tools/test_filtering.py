# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx",
# ]
# ///

import httpx
import sys

API_URL = "http://localhost:8000"

def test_filtering():
    print("Testing Ingredient Filtering...")
    
    # 1. Get all ingredients
    try:
        response = httpx.get(f"{API_URL}/recipes/ingredients")
        response.raise_for_status()
        ingredients = response.json()
        print(f"Available ingredients: {ingredients}")
    except Exception as e:
        print(f"Error fetching ingredients: {e}")
        return

    if not ingredients:
        print("No ingredients found to test filtering.")
        return

    # 2. Filter by the first ingredient
    first_ing = ingredients[0]
    print(f"Filtering by '{first_ing}'...")
    try:
        response = httpx.get(f"{API_URL}/recipes/", params={"ingredients": [first_ing]})
        response.raise_for_status()
        recipes = response.json()
        print(f"Found {len(recipes)} recipes with '{first_ing}':")
        for r in recipes:
            print(f"  - {r['name']}")
            # Verify ingredient is present
            has_ing = any(first_ing.lower() in i['name'].lower() for i in r['ingredients'])
            if not has_ing:
                print(f"    ERROR: Recipe {r['name']} does not contain '{first_ing}'!")
    except Exception as e:
        print(f"Error filtering recipes: {e}")

if __name__ == "__main__":
    test_filtering()
