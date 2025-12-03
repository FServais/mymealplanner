# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx",
# ]
# ///

import httpx
import json

API_URL = "http://localhost:8000"

def test_shopping_list():
    print("Testing Shopping List Aggregation...")

    # 1. Get some recipes to use
    try:
        response = httpx.get(f"{API_URL}/recipes/")
        response.raise_for_status()
        recipes = response.json()
        if len(recipes) < 2:
            print("Not enough recipes to test aggregation. Please import more.")
            return

        # Pick first two recipes
        recipe_ids = [r['id'] for r in recipes[:2]]
        print(f"Generating shopping list for recipes: {recipe_ids}")

        # 2. Generate shopping list
        response = httpx.post(f"{API_URL}/meal-planner/generate-shopping-list", json=recipe_ids)
        response.raise_for_status()
        shopping_list = response.json()

        print("Shopping List:")
        for item in shopping_list:
            print(f"  - {item['name']}: {item['quantity']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_shopping_list()
