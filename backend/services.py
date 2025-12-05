import os
import uuid
from typing import List
import pypdf
import io
import json
from openai import (
    OpenAI,
    AuthenticationError,
    RateLimitError,
    BadRequestError,
    APIConnectionError,
)
from sqlalchemy.orm import Session
import google.generativeai as genai

def process_pdf_import_task(task_id: str, file_content: bytes, filename: str, provider: str = "openai"):
    """
    Background task to process PDF import.
    Updates the database with progress and result.

    Args:
        task_id: Unique identifier for the import task
        file_content: Raw PDF file bytes
        filename: Original filename of the PDF
        provider: LLM provider to use ("openai" or "gemini", default: "openai")
    """
    from database import SessionLocal
    from models import ImportTask
    
    print(f"[PDF Import {task_id}] Starting background task for file: {filename} (provider: {provider})")
    
    db = SessionLocal()
    try:
        # Update status to processing
        print(f"[PDF Import {task_id}] Updating status to 'processing'")
        task = db.query(ImportTask).filter(ImportTask.id == task_id).first()
        if task:
            task.status = "processing"
            db.commit()
            print(f"[PDF Import {task_id}] Status updated to 'processing'")
        else:
            print(f"[PDF Import {task_id}] ERROR: Task not found in database!")
            return
        
        # Extract text from PDF
        print(f"[PDF Import {task_id}] Extracting text from PDF ({len(file_content)} bytes)")
        text = extract_text_from_pdf(file_content)
        if not text:
            print(f"[PDF Import {task_id}] ERROR: Could not extract text from PDF")
            task.status = "failed"
            task.error = "Could not extract text from PDF"
            db.commit()
            return
        
        print(f"[PDF Import {task_id}] Extracted {len(text)} characters from PDF")

        # Parse recipe with LLM
        print(f"[PDF Import {task_id}] Parsing recipe with {provider.upper()} LLM...")
        recipe_data = parse_recipe_with_llm(text, provider=provider)
        
        # Check if parsing resulted in an error
        if recipe_data.get("name", "").startswith("Error"):
            error_msg = recipe_data.get("description", "Unknown error occurred")
            print(f"[PDF Import {task_id}] ERROR: LLM parsing failed: {error_msg}")
            task.status = "failed"
            task.error = error_msg
            db.commit()
            return
        
        print(f"[PDF Import {task_id}] Successfully parsed recipe: {recipe_data.get('name')}")
        recipe_data["source_file"] = filename
        
        # Save result
        print(f"[PDF Import {task_id}] Saving result to database")
        task.status = "completed"
        task.result = json.dumps(recipe_data)
        db.commit()
        print(f"[PDF Import {task_id}] Task completed successfully")
        
    except Exception as e:
        print(f"[PDF Import {task_id}] EXCEPTION: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        task = db.query(ImportTask).filter(ImportTask.id == task_id).first()
        if task:
            task.status = "failed"
            task.error = str(e)
            db.commit()
    finally:
        db.close()
        print(f"[PDF Import {task_id}] Background task finished")


def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

RAW_ING_SYSTEM_PROMPT = """
You are a specialized ingredient line extractor.

Goal:
From raw text extracted from a recipe PDF, capture ALL lines that look like ingredients,
without filtering by serving size.

What to capture:
- Any line or row that looks like an ingredient: typically contains a quantity and a food name.
- Include lines from ingredient sections and tables (e.g. with columns for 2 pers, 3-4 pers, etc.).
- Ignore headers like "Ingrédients", "Dans la box", "Préparation", page numbers, disclaimers.

For each ingredient line:
- raw_text: the raw line or row as it appears in the text (you may join broken lines).
- serving_hint: any hint about serving size if you can infer it from the context, such as:
    "2 pers", "2 personnes", "2p", "3-4 pers", etc.
  If there is no clear hint, use null.

Output:
- Always respond by CALLING the extract_raw_ingredients function with arguments matching its JSON schema.
- Do NOT answer in free text.
""".strip()

RAW_ING_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "extract_raw_ingredients",
            "description": "Capture all raw ingredient-like lines from the recipe text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lines": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "raw_text": {
                                    "type": "string",
                                    "description": "Raw ingredient line or row as seen in the text."
                                },
                                "serving_hint": {
                                    "type": ["string", "null"],
                                    "description": "Serving size hint for this line, e.g. '2 pers', '3-4 pers', or null."
                                }
                            },
                            "required": ["raw_text", "serving_hint"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["lines"],
                "additionalProperties": False
            }
        }
    }
]

PARSE_SYSTEM_PROMPT = """
You are a specialized recipe parser.

Goal:
From raw text extracted from a PDF, and from a list of raw ingredient lines,
extract:
1. The clean recipe name.
2. A structured list of ingredients for 2 people only.
3. A clean, ordered list of instructions.

You are given:
- The full raw recipe text (noisy PDF extraction).
- A pre-extracted list of raw ingredient lines with serving-size hints.

Use the raw ingredient lines as your primary source for ingredients to avoid missing any.

Recipe name rules:
- Identify the main recipe title.
- Clean up capitalization, extra whitespace, duplicates, and layout noise.
- Prefer the most prominent or repeated title.
- Output a short, human-friendly name.

Ingredients rules:
- The text may contain quantities for several serving sizes (e.g., 2 people, 3–4 people, etc.).
- Extract ONLY the ingredient quantities that apply to 2 people, exactly as written in the text.
- For each ingredient, fill:
  - name: ingredient description. Clean up the name by removing country codes or suffixes indicating origin (e.g., "Oignon BE" -> "Oignon", "Carottes FR" -> "Carottes").
  - quantity: the quantity for 2 people as written (e.g., "200 g", "1 oignon", "1/2 sachet").
  - unit: the explicit unit ("g", "ml", "tbsp", etc.) if present, otherwise null.
- Do NOT scale or convert quantities.
- Do NOT invent quantities; if a 2-person quantity is missing, skip that ingredient.

Instructions rules:
- Extract instructions as an ordered list of cooking steps.
- Merge broken lines within the same step into a coherent sentence or short paragraph.
- Remove numbering artifacts at the start of each step (e.g., "1)", "2.", "-").
- Remove unrelated text such as headers, footers, page numbers, disclaimers, and brand/box notes.

Output:
- Always respond by CALLING the extract_recipe function with arguments matching its JSON schema.
- Do NOT answer in free text: the response must be a function call.
""".strip()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "extract_recipe",
            "description": "Extracts the recipe name, structured ingredients (for 2 people), and instructions from raw recipe text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipe_name": {
                        "type": "string",
                        "description": "The cleaned name/title of the recipe."
                    },
                    "ingredients": {
                        "type": "array",
                        "description": "List of ingredients for 2 people only, as extracted from the text.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name/description of the ingredient."
                                },
                                "quantity": {
                                    "type": "string",
                                    "description": "Quantity as written in the text for 2 people (e.g., '200 g', '1 oignon', '1/2 sachet')."
                                },
                                "unit": {
                                    "type": ["string", "null"],
                                    "description": "Unit of the quantity (e.g., 'g', 'ml', 'tbsp'), or null if not specified."
                                }
                            },
                            "required": ["name", "quantity", "unit"],
                            "additionalProperties": False
                        }
                    },
                    "instructions": {
                        "type": "array",
                        "description": "Ordered list of cooking steps.",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["recipe_name", "ingredients", "instructions"],
                "additionalProperties": False
            }
        }
    }
]

def format_raw_lines_for_prompt(raw_lines):
    """
    Formats a list of raw ingredient lines into a string for the LLM prompt.
    Each line is prefixed with its index and serving hint.
    """
    formatted = []
    for i, line in enumerate(raw_lines, start=1):
        hint = line["serving_hint"] or "unknown"
        formatted.append(f"{i}. [{hint}] {line['raw_text']}")
    return "\n".join(formatted)

def parse_recipe_with_llm(text: str, api_key: str = None, provider: str = "openai"):
    """
    Parses recipe text using an LLM to extract structured recipe data.

    This function dispatches to provider-specific implementations.

    Args:
        text: Raw text extracted from a recipe PDF
        api_key: API key for the provider (defaults to environment variable)
        provider: LLM provider to use ("openai" or "gemini", default: "openai")

    Returns:
        dict: A dictionary containing:
            - name (str): The recipe name
            - description (str): Recipe description
            - ingredients (list): List of dicts with 'name' and 'quantity' keys
            - instructions (list): List of dicts with 'step_number' and 'text' keys
    """
    provider = provider.lower().strip()

    if provider == "gemini":
        return _parse_with_gemini(text, api_key)
    else:
        return _parse_with_openai(text, api_key)


def _parse_with_openai(text: str, api_key: str = None):
    """
    Parses recipe text using OpenAI's API.

    Uses a two-stage process:
    1. Extract raw ingredient lines with serving hints
    2. Parse the full recipe
    """
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("No OpenAI API key provided. Returning mock data.")
        return {
            "name": "Mock Recipe (No API Key)",
            "description": "Please provide an OPENAI_API_KEY to use the real extraction.",
            "ingredients": [
                {"name": "Mock Ingredient", "quantity": "1 unit"}
            ],
            "instructions": [
                {"step_number": 1, "text": "Add API key to environment variables."}
            ]
        }

    client = OpenAI(api_key=api_key)

    try:
        # Stage 1: Extract raw ingredient lines
        raw_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": RAW_ING_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Here is the text extracted from my PDF:\n\n{text}"
                },
            ],
            tools=RAW_ING_TOOLS,
            tool_choice={
                "type": "function",
                "function": {"name": "extract_raw_ingredients"},
            },
            timeout=600.0,
        )

        tool_call = raw_response.choices[0].message.tool_calls[0]
        raw_args = json.loads(tool_call.function.arguments)
        raw_lines = raw_args["lines"]
        raw_lines_text = format_raw_lines_for_prompt(raw_lines)

        # Stage 2: Parse full recipe
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PARSE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Here is the full text extracted from my PDF:\n\n"
                        f"{text}\n\n"
                        "Here is a pre-extracted list of raw ingredient lines with serving hints:\n\n"
                        f"{raw_lines_text}"
                    ),
                },
            ],
            tools=TOOLS,
            tool_choice={
                "type": "function",
                "function": {"name": "extract_recipe"}
            },
            timeout=600.0,
        )

        tool_call = response.choices[0].message.tool_calls[0]
        function_args = json.loads(tool_call.function.arguments)

        return _transform_llm_response(function_args)

    except AuthenticationError as e:
        error_msg = "Authentication failed: Invalid API key or expired token"
        print(f"OpenAI AuthenticationError: {e}")
        return _error_response("Error: Authentication Failed", error_msg)

    except RateLimitError as e:
        error_msg = "Rate limit exceeded. Please try again later."
        print(f"OpenAI RateLimitError: {e}")
        return _error_response("Error: Rate Limit Exceeded", error_msg)

    except BadRequestError as e:
        error_msg = f"Invalid request: {str(e)}"
        print(f"OpenAI BadRequestError: {e}")
        return _error_response("Error: Invalid Request", error_msg)

    except APIConnectionError as e:
        error_msg = "Failed to connect to OpenAI API. Check network connection."
        print(f"OpenAI APIConnectionError: {e}")
        return _error_response("Error: Connection Failed", error_msg)

    except (KeyError, IndexError, json.JSONDecodeError) as e:
        error_msg = f"Failed to parse LLM response: {str(e)}"
        print(f"Response parsing error: {e}")
        return _error_response("Error: Invalid LLM Response", error_msg)

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"Unexpected error parsing recipe with OpenAI: {e}")
        return _error_response("Error Parsing Recipe", error_msg)


def _parse_with_gemini(text: str, api_key: str = None):
    """
    Parses recipe text using Google Gemini's API.

    Uses a two-stage process similar to OpenAI:
    1. Extract raw ingredient lines with serving hints
    2. Parse the full recipe
    """
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("No Gemini API key provided. Returning mock data.")
        return {
            "name": "Mock Recipe (No API Key)",
            "description": "Please provide a GEMINI_API_KEY to use the real extraction.",
            "ingredients": [
                {"name": "Mock Ingredient", "quantity": "1 unit"}
            ],
            "instructions": [
                {"step_number": 1, "text": "Add API key to environment variables."}
            ]
        }

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        # Stage 1: Extract raw ingredient lines
        raw_prompt = f"""{RAW_ING_SYSTEM_PROMPT}

Here is the text extracted from my PDF:

{text}

Respond with a JSON object containing a "lines" array. Each item should have:
- "raw_text": the ingredient line as seen in the text
- "serving_hint": serving size hint like "2 pers" or null if unknown

Example response:
{{"lines": [{{"raw_text": "200g chicken", "serving_hint": "2 pers"}}, {{"raw_text": "1 onion", "serving_hint": null}}]}}
"""

        raw_response = model.generate_content(
            raw_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            ),
        )

        raw_text = raw_response.text
        raw_args = json.loads(raw_text)
        raw_lines = raw_args.get("lines", [])
        raw_lines_text = format_raw_lines_for_prompt(raw_lines)

        # Stage 2: Parse full recipe
        parse_prompt = f"""{PARSE_SYSTEM_PROMPT}

Here is the full text extracted from my PDF:

{text}

Here is a pre-extracted list of raw ingredient lines with serving hints:

{raw_lines_text}

Respond with a JSON object containing:
- "recipe_name": string
- "ingredients": array of {{"name": string, "quantity": string, "unit": string or null}}
- "instructions": array of strings (cooking steps)

Example response:
{{"recipe_name": "Pasta Carbonara", "ingredients": [{{"name": "Spaghetti", "quantity": "200", "unit": "g"}}], "instructions": ["Boil pasta", "Mix eggs with cheese"]}}
"""

        response = model.generate_content(
            parse_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )

        function_args = json.loads(response.text)

        return _transform_llm_response(function_args)

    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse Gemini response as JSON: {str(e)}"
        print(f"Gemini JSON parsing error: {e}")
        return _error_response("Error: Invalid LLM Response", error_msg)

    except Exception as e:
        error_msg = f"Gemini API error: {str(e)}"
        print(f"Unexpected error parsing recipe with Gemini: {e}")
        return _error_response("Error Parsing Recipe", error_msg)


def _transform_llm_response(function_args: dict) -> dict:
    """
    Transforms the raw LLM response into the RecipeCreate schema.
    """
    recipe_data = {
        "name": function_args.get("recipe_name") or "Unnamed Recipe",
        "description": "Imported from PDF via LLM",
        "ingredients": [],
        "instructions": []
    }

    for ing in function_args.get("ingredients", []):
        name = ing.get("name")
        if not name:
            continue  # Skip ingredients without a name

        qty = ing.get("quantity", "") or ""
        unit = ing.get("unit")
        if unit and unit.lower() not in qty.lower():
            qty = f"{qty} {unit}"

        recipe_data["ingredients"].append({
            "name": str(name),
            "quantity": str(qty) if qty else ""
        })

    for idx, inst in enumerate(function_args.get("instructions", [])):
        if inst:  # Skip empty instructions
            recipe_data["instructions"].append({
                "step_number": idx + 1,
                "text": str(inst)
        })

    return recipe_data


def _error_response(name: str, description: str) -> dict:
    """
    Creates a standardized error response.
    """
    return {
        "name": name,
        "description": description,
        "ingredients": [],
        "instructions": []
    }

import re
from fractions import Fraction

def parse_quantity(quantity_str: str):
    """
    Parses a quantity string into (amount, unit).
    Examples:
    "200 g" -> (200.0, "g")
    "1/2 cup" -> (0.5, "cup")
    "2" -> (2.0, "")
    "onion" -> (1.0, "onion") # Fallback if no number found? No, usually ingredient name is separate.
    """
    if not quantity_str:
        return 0.0, ""

    quantity_str = quantity_str.strip().lower()

    # Match number (int, float, or fraction) at start
    # Regex: starts with digits, optional decimal or fraction part
    match = re.match(r"^(\d+(?:/\d+)?|\d+(?:\.\d+)?)\s*(.*)$", quantity_str)

    if match:
        amount_str, unit = match.groups()
        try:
            if "/" in amount_str:
                amount = float(Fraction(amount_str))
            else:
                amount = float(amount_str)
            return amount, unit.strip()
        except ValueError:
            pass

    return 0.0, quantity_str

def generate_shopping_list(recipes: List[dict]) -> List[dict]:
    shopping_list = {}

    for recipe in recipes:
        for ingredient in recipe.ingredients:
            name = ingredient.name.lower().strip()
            qty_str = ingredient.quantity

            amount, unit = parse_quantity(qty_str)

            # Key for aggregation: (name, unit)
            # This avoids merging "grams" with "pieces" if conversion isn't possible
            key = (name, unit)

            if key in shopping_list:
                shopping_list[key] += amount
            else:
                shopping_list[key] = amount

    # Format for display
    final_list = []
    for (name, unit), total_amount in shopping_list.items():
        # Format amount: remove .0 if integer
        if total_amount.is_integer():
            amount_display = str(int(total_amount))
        else:
            amount_display = f"{total_amount:.2f}".rstrip('0').rstrip('.')

        full_quantity = f"{amount_display} {unit}".strip()
        final_list.append({"name": name, "quantity": full_quantity})

    # Sort by name
    final_list.sort(key=lambda x: x['name'])

    return final_list

def suggest_ingredient_duplicates(ingredients: List[str], provider: str = "gemini") -> List[dict]:
    """
    Uses LLM to find potential duplicate ingredients in a list.
    Returns a list of groups, where each group has a 'target' (suggested canonical name)
    and 'sources' (list of variations to merge).

    Args:
        ingredients: List of ingredient names to analyze
        provider: LLM provider to use ("openai" or "gemini", default: "openai")
    """
    print(f"[suggest_ingredient_duplicates] Starting with {len(ingredients)} ingredients (provider: {provider})", flush=True)

    if not ingredients:
        print("[suggest_ingredient_duplicates] No ingredients provided, returning empty list", flush=True)
        return []

    # Hybrid approach: prefix grouping + similarity within groups
    # This is O(n) for grouping + O(k²) for similarity within each group (where k << n)
    print("[suggest_ingredient_duplicates] Pre-filtering with prefix grouping + similarity...", flush=True)

    from collections import defaultdict
    
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]
    
    def similarity_ratio(s1: str, s2: str) -> float:
        """Calculate similarity ratio (0.0 to 1.0) based on Levenshtein distance."""
        s1_lower, s2_lower = s1.lower(), s2.lower()
        max_len = max(len(s1_lower), len(s2_lower))
        if max_len == 0:
            return 1.0
        distance = levenshtein_distance(s1_lower, s2_lower)
        return 1.0 - (distance / max_len)
    
    # Group ingredients by their first 2 characters (lowercased) - broader groups
    prefix_groups = defaultdict(list)
    for ing in ingredients:
        prefix = ing.lower()[:2] if len(ing) >= 2 else ing.lower()
        prefix_groups[prefix].append(ing)
    
    # Within each prefix group, find pairs with high similarity
    SIMILARITY_THRESHOLD = 0.7
    potential_duplicates = set()
    
    for prefix, group in prefix_groups.items():
        if len(group) >= 2:
            # Compare all pairs within this group
            for i, ing1 in enumerate(group):
                for ing2 in group[i+1:]:
                    if similarity_ratio(ing1, ing2) >= SIMILARITY_THRESHOLD:
                        potential_duplicates.add(ing1)
                        potential_duplicates.add(ing2)
    
    print(f"[suggest_ingredient_duplicates] Found {len(potential_duplicates)} potential duplicates from similarity matching", flush=True)

    # If we found potential duplicates, only send those to the LLM
    if potential_duplicates:
        # Convert to list and remove any exact duplicates (case-insensitive)
        seen = set()
        filtered_ingredients = []
        for ing in sorted(potential_duplicates):
            ing_lower = ing.lower()
            if ing_lower not in seen:
                seen.add(ing_lower)
                filtered_ingredients.append(ing)
        print(f"[suggest_ingredient_duplicates] Filtered to {len(filtered_ingredients)} unique ingredients (from {len(ingredients)} total)", flush=True)
        
        # Limit to 200 ingredients to avoid timeout
        MAX_INGREDIENTS = 200
        if len(filtered_ingredients) > MAX_INGREDIENTS:
            print(f"[suggest_ingredient_duplicates] Limiting to {MAX_INGREDIENTS} ingredients to avoid timeout", flush=True)
            filtered_ingredients = filtered_ingredients[:MAX_INGREDIENTS]
    else:
        print("[suggest_ingredient_duplicates] No similar ingredients found, returning empty list", flush=True)
        return []

    provider = provider.lower().strip()
    if provider == "gemini":
        return _suggest_duplicates_gemini(filtered_ingredients)
    else:
        return _suggest_duplicates_openai(filtered_ingredients)


DUPLICATE_PROMPT = """
You are a data cleaning assistant for a recipe database.
I will provide a list of ingredient names that are potentially similar.
Your task is to identify synonyms, misspellings, plural variations, or language variations that refer to the same ingredient.
Group them together and suggest a single "canonical" name for the group (preferably the most common, simple, singular form in French or English, matching the input language).

Ignore ingredients that are distinct. Only output groups where there are at least 2 variations.

Output format: JSON object with a key "duplicates" containing a list of objects, each with:
- "target": string (the canonical name)
- "sources": list of strings (the variations found in the input list, INCLUDING the target if it was in the list)

Example input: ["Tomate", "Tomates", "Tomato", "Beef", "Boeuf"]
Example output: {
    "duplicates": [
        {"target": "Tomate", "sources": ["Tomate", "Tomates", "Tomato"]},
        {"target": "Boeuf", "sources": ["Beef", "Boeuf"]}
    ]
}
"""


def _suggest_duplicates_openai(filtered_ingredients: List[str]) -> List[dict]:
    """
    Uses OpenAI to find potential duplicate ingredients.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[suggest_duplicates_openai] ERROR: No API key provided.")
        return []

    print("[suggest_duplicates_openai] API key found, initializing OpenAI client")
    client = OpenAI(api_key=api_key)

    ingredients_text = json.dumps(filtered_ingredients)
    print(f"[suggest_duplicates_openai] Prepared ingredient list, length: {len(ingredients_text)} chars")

    try:
        print("[suggest_duplicates_openai] Calling OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": DUPLICATE_PROMPT},
                {"role": "user", "content": f"Here is the list of ingredients:\n{ingredients_text}"}
            ],
            response_format={"type": "json_object"}
        )

        print("[suggest_duplicates_openai] Received response from OpenAI")
        content = response.choices[0].message.content
        print(f"[suggest_duplicates_openai] Response content: {content[:200]}...")

        result = json.loads(content)
        print(f"[suggest_duplicates_openai] Parsed JSON result, keys: {result.keys()}", flush=True)

        duplicates = result.get("duplicates", [])
        print(f"[suggest_duplicates_openai] Found {len(duplicates)} duplicate groups before filtering", flush=True)
        
        # Filter out groups with less than 2 sources (can't merge a single item)
        valid_duplicates = [d for d in duplicates if len(d.get("sources", [])) >= 2]
        print(f"[suggest_duplicates_openai] {len(valid_duplicates)} groups have 2+ sources", flush=True)

        return valid_duplicates

    except Exception as e:
        print(f"[suggest_duplicates_openai] ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []


def _suggest_duplicates_gemini(filtered_ingredients: List[str]) -> List[dict]:
    """
    Uses Google Gemini to find potential duplicate ingredients.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[suggest_duplicates_gemini] ERROR: No API key provided.")
        return []

    print("[suggest_duplicates_gemini] API key found, initializing Gemini client")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        ingredients_text = json.dumps(filtered_ingredients)
        print(f"[suggest_duplicates_gemini] Prepared ingredient list, length: {len(ingredients_text)} chars")

        prompt = f"""{DUPLICATE_PROMPT}

Here is the list of ingredients:
{ingredients_text}
"""

        print("[suggest_duplicates_gemini] Calling Gemini API...")
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            ),
        )

        print("[suggest_duplicates_gemini] Received response from Gemini")
        content = response.text
        print(f"[suggest_duplicates_gemini] Response content length: {len(content)} chars")

        # Sanitize invalid unicode escapes (e.g., \uXXXX with invalid hex)
        import re
        def fix_invalid_unicode(match):
            try:
                # Try to decode the unicode escape
                return match.group(0).encode().decode('unicode_escape')
            except:
                # If invalid, just remove the escape
                return ""
        
        # Remove invalid \uXXXX escapes
        content = re.sub(r'\\u[0-9a-fA-F]{0,3}(?![0-9a-fA-F])', '', content)

        result = json.loads(content)
        print(f"[suggest_duplicates_gemini] Parsed JSON result, keys: {result.keys()}", flush=True)

        duplicates = result.get("duplicates", [])
        print(f"[suggest_duplicates_gemini] Found {len(duplicates)} duplicate groups before filtering", flush=True)
        
        # Filter out groups with less than 2 sources (can't merge a single item)
        valid_duplicates = [d for d in duplicates if len(d.get("sources", [])) >= 2]
        print(f"[suggest_duplicates_gemini] {len(valid_duplicates)} groups have 2+ sources", flush=True)

        return valid_duplicates

    except json.JSONDecodeError as e:
        print(f"[suggest_duplicates_gemini] JSON parsing error: {e}")
        print(f"[suggest_duplicates_gemini] Raw content (first 500 chars): {content[:500] if 'content' in dir() else 'N/A'}")
        return []

    except Exception as e:
        print(f"[suggest_duplicates_gemini] ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []
