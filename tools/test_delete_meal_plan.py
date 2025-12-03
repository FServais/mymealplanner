# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx",
# ]
# ///

import httpx
import json

API_URL = "http://localhost:8000"

def test_delete_meal_plan():
    print("Testing Meal Plan Deletion...")

    # 1. Create a dummy meal plan
    try:
        response = httpx.get(f"{API_URL}/recipes/")
        recipes = response.json()
        if not recipes:
            print("No recipes found.")
            return

        recipe_ids = [recipes[0]['id']]
        plan_data = {"name": "To Be Deleted", "recipe_ids": recipe_ids}

        response = httpx.post(f"{API_URL}/meal-plans/", json=plan_data)
        response.raise_for_status()
        created_plan = response.json()
        plan_id = created_plan['id']
        print(f"Created Meal Plan: ID={plan_id}")

        # 2. Delete it
        print(f"Deleting Meal Plan ID={plan_id}...")
        response = httpx.delete(f"{API_URL}/meal-plans/{plan_id}")
        response.raise_for_status()
        print("Deletion successful (204 No Content).")

        # 3. Verify it's gone
        response = httpx.get(f"{API_URL}/meal-plans/{plan_id}")
        if response.status_code == 404:
            print("Verification successful: Meal plan not found.")
        else:
            print(f"Verification failed: Status {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_delete_meal_plan()
