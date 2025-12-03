# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx",
# ]
# ///

import httpx
import json

API_URL = "http://localhost:8000"

def test_meal_plans():
    print("Testing Meal Plan API...")

    # 1. Get recipes to include
    try:
        response = httpx.get(f"{API_URL}/recipes/")
        response.raise_for_status()
        recipes = response.json()
        if not recipes:
            print("No recipes found. Cannot test meal plan creation.")
            return

        recipe_ids = [r['id'] for r in recipes[:2]]
        print(f"Creating meal plan with recipes: {recipe_ids}")

        # 2. Create Meal Plan
        plan_data = {
            "name": "Test Meal Plan",
            "recipe_ids": recipe_ids
        }
        response = httpx.post(f"{API_URL}/meal-plans/", json=plan_data)
        response.raise_for_status()
        created_plan = response.json()
        print(f"Created Meal Plan: ID={created_plan['id']}, Name='{created_plan['name']}'")

        # 3. List Meal Plans
        response = httpx.get(f"{API_URL}/meal-plans/")
        response.raise_for_status()
        plans = response.json()
        print(f"Found {len(plans)} meal plans.")

        # 4. Get Specific Meal Plan
        plan_id = created_plan['id']
        response = httpx.get(f"{API_URL}/meal-plans/{plan_id}")
        response.raise_for_status()
        fetched_plan = response.json()
        print(f"Fetched Plan: {fetched_plan['name']}")
        print(f"Recipes in plan: {[r['name'] for r in fetched_plan['recipes']]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_meal_plans()
