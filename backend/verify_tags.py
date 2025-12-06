import requests
import json

BASE_URL = "http://localhost:8082"

def test_tags_support():
    print("Testing Tags Support...")

    # 1. Create a recipe with tags
    recipe_data = {
        "name": "Test Recipe With Tags",
        "description": "A test recipe",
        "ingredients": [{"name": "Ingredient 1", "quantity": "1"}],
        "instructions": [{"step_number": 1, "text": "Mix"}],
        "tags": [{"name": "Tag1", "color": "#ff0000"}, "Tag2"]
    }
    
    print("Creating recipe...")
    res = requests.post(f"{BASE_URL}/recipes/", json=recipe_data)
    if res.status_code != 200:
        print(f"Failed to create recipe: {res.text}")
        return
    
    recipe = res.json()
    print(f"Created recipe ID: {recipe['id']}")
    
    # Verify tags are returned with colors
    returned_tags = {t['name']: t.get('color') for t in recipe.get('tags', [])}
    print(f"Returned Tags: {returned_tags}")
    
    if "Tag1" not in returned_tags or "Tag2" not in returned_tags:
        print(f"FAILURE: Missing tags")
        return
        
    if returned_tags["Tag1"] != "#ff0000":
         print(f"FAILURE: Tag1 color incorrect. Expected #ff0000, got {returned_tags['Tag1']}")

    print("SUCCESS: Tags created correctly with colors.")

    # 2. Get recipe by ID and check tags
    print("Fetching recipe by ID...")
    res = requests.get(f"{BASE_URL}/recipes/{recipe['id']}")
    fetched_recipe = res.json()
    returned_tags = {t['name']: t.get('color') for t in fetched_recipe.get('tags', [])}
    if "Tag1" not in returned_tags:
        print(f"FAILURE: Expected Tag1")
        return
    print("SUCCESS: Tags retrieved correctly.")

    # 3. Create another recipe with overlapping tags
    recipe_data_2 = {
        "name": "Test Recipe 2",
        "ingredients": [{"name": "Ingredient 2", "quantity": "1"}],
        "instructions": [{"step_number": 1, "text": "Mix"}],
        "tags": ["Tag2", "Tag3"]
    }
    res = requests.post(f"{BASE_URL}/recipes/", json=recipe_data_2)
    recipe2 = res.json()
    print(f"Created recipe 2 ID: {recipe2['id']}")

    # 4. Filter by Tag1 -> Should get only recipe 1
    print("Filtering by Tag1...")
    res = requests.get(f"{BASE_URL}/recipes/", params={"tags": ["Tag1"]})
    recipes = res.json()
    ids = [r['id'] for r in recipes]
    if recipe['id'] in ids and recipe2['id'] not in ids:
        print("SUCCESS: Filter by Tag1 correct.")
    else:
        print(f"FAILURE: Filter by Tag1 returned IDs: {ids}")

    # 5. Filter by Tag2 -> Should get both
    print("Filtering by Tag2...")
    res = requests.get(f"{BASE_URL}/recipes/", params={"tags": ["Tag2"]})
    recipes = res.json()
    ids = [r['id'] for r in recipes]
    if recipe['id'] in ids and recipe2['id'] in ids:
        print("SUCCESS: Filter by Tag2 correct.")
    else:
        print(f"FAILURE: Filter by Tag2 returned IDs: {ids}")

    # 6. Filter by Tag3 -> Should get only recipe 2
    print("Filtering by Tag3...")
    res = requests.get(f"{BASE_URL}/recipes/", params={"tags": ["Tag3"]})
    recipes = res.json()
    ids = [r['id'] for r in recipes]
    if recipe['id'] not in ids and recipe2['id'] in ids:
        print("SUCCESS: Filter by Tag3 correct.")
    else:
        print(f"FAILURE: Filter by Tag3 returned IDs: {ids}")

    # 7. Get all tags
    print("Fetching all tags...")
    res = requests.get(f"{BASE_URL}/recipes/tags")
    all_tags = res.json()
    all_tag_names = [t['name'] for t in all_tags]
    if "Tag1" in all_tag_names and "Tag2" in all_tag_names:
        print("SUCCESS: All tags retrieved.")
    else:
        print(f"FAILURE: Missing tags in list: {all_tag_names}")

    # Cleanup
    print("Cleaning up...")
    requests.delete(f"{BASE_URL}/recipes/{recipe['id']}")
    requests.delete(f"{BASE_URL}/recipes/{recipe2['id']}")
    print("Done.")

if __name__ == "__main__":
    try:
        test_tags_support()
    except Exception as e:
        print(f"An error occurred: {e}")
