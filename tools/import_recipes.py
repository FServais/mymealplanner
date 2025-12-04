# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx",
# ]
# ///

import os
import argparse
import httpx
import time
import re
from pathlib import Path

API_URL = "https://meal.servais-devos.com"

def extract_version(filename):
    """Extracts the number XXX from [letter]XXX.pdf"""
    match = re.search(r'[a-zA-Z](\d+)', filename)
    if match:
        return int(match.group(1))
    return 0

def check_if_exists(filename):
    """Checks if the recipe with this source_file already exists in DB."""
    try:
        response = httpx.get(f"{API_URL}/recipes/", params={"source_file": filename})
        response.raise_for_status()
        recipes = response.json()
        return len(recipes) > 0
    except Exception:
        return False

def import_recipe(file_path: Path, provider: str = "openai"):
    print(f"Processing {file_path.name} (provider: {provider})...")

    # 1. Submit PDF for processing
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/pdf")}
            response = httpx.post(
                f"{API_URL}/recipes/import/pdf",
                files=files,
                params={"provider": provider},
                timeout=30.0
            )
            response.raise_for_status()
            task_data = response.json()
            task_id = task_data.get("task_id")
            print(f"  - Submitted for processing (task ID: {task_id})")
    except httpx.HTTPStatusError as e:
        print(f"  - HTTP Error {e.response.status_code}: {e.response.text}")
        return
    except httpx.TimeoutException:
        print(f"  - Error: Request timeout during submission")
        return
    except httpx.RequestError as e:
        print(f"  - Error connecting to API: {e}")
        return
    except Exception as e:
        print(f"  - Error submitting PDF: {e}")
        return

    # 2. Poll for completion
    max_attempts = 180  # 6 minutes max
    attempts = 0
    recipe_data = None

    while attempts < max_attempts:
        try:
            status_response = httpx.get(f"{API_URL}/recipes/import/status/{task_id}", timeout=10.0)
            status_response.raise_for_status()
            task = status_response.json()

            if task["status"] == "completed":
                recipe_data = task.get("result")
                print(f"  - Successfully extracted: {recipe_data.get('name')}")
                break
            elif task["status"] == "failed":
                error_msg = task.get("error", "Unknown error")
                print(f"  - Error parsing recipe: {error_msg}")
                return
            else:
                # Still processing
                time.sleep(2)
                attempts += 1
        except Exception as e:
            print(f"  - Error polling status: {e}")
            return

    if recipe_data is None:
        print(f"  - Error: Processing timeout (exceeded 6 minutes)")
        return

    # 3. Save to Database
    try:
        create_response = httpx.post(f"{API_URL}/recipes/", json=recipe_data, timeout=60.0)
        create_response.raise_for_status()
        print(f"  - Successfully saved to database with ID: {create_response.json().get('id')}")
    except Exception as e:
        print(f"  - Error saving recipe: {e}")

def main():
    parser = argparse.ArgumentParser(description="Bulk import recipes from PDFs.")
    parser.add_argument("directory", type=str, help="Directory containing PDF files")
    parser.add_argument("--start", type=int, help="Start from this version number (inclusive)")
    parser.add_argument("--end", type=int, help="End at this version number (inclusive)")
    parser.add_argument("--resume", action="store_true", help="Skip files that are already in the database")
    parser.add_argument("--provider", type=str, default="openai", choices=["openai", "gemini"],
                        help="LLM provider to use (default: openai)")

    args = parser.parse_args()

    directory = Path(args.directory)
    if not directory.exists():
        print(f"Directory not found: {directory}")
        return

    # Get all PDF files
    pdf_files = list(directory.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in the directory.")
        return

    # Sort by version number
    pdf_files.sort(key=lambda p: extract_version(p.name))

    print(f"Found {len(pdf_files)} PDF files.")

    # Filter by range
    if args.start is not None:
        pdf_files = [p for p in pdf_files if extract_version(p.name) >= args.start]
    if args.end is not None:
        pdf_files = [p for p in pdf_files if extract_version(p.name) <= args.end]

    print(f"Processing {len(pdf_files)} files after filtering.")

    for pdf_file in pdf_files:
        if args.resume:
            if check_if_exists(pdf_file.name):
                print(f"Skipping {pdf_file.name} (already exists)")
                continue

        import_recipe(pdf_file, provider=args.provider)
        time.sleep(1) # Be nice to the API/LLM

if __name__ == "__main__":
    main()
