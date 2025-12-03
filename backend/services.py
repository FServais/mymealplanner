import os
from typing import List
import pypdf
import io
import json
from openai import OpenAI

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
    formatted = []
    for i, line in enumerate(raw_lines, start=1):
        hint = line["serving_hint"] or "unknown"
        formatted.append(f"{i}. [{hint}] {line['raw_text']}")
    return "\n".join(formatted)

def parse_recipe_with_llm(text: str, api_key: str = None, provider: str = "openai"):
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("No API key provided. Returning mock data.")
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
        raw_response = client.chat.completions.create(
            model="gpt-5-mini",
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

        response = client.chat.completions.create(
            model="gpt-5-nano",
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
            timeout=600.0,  # 2 minute timeout
        )

        tool_call = response.choices[0].message.tool_calls[0]
        function_args = json.loads(tool_call.function.arguments)

        # Transform to RecipeCreate schema
        recipe_data = {
            "name": function_args.get("recipe_name"),
            "description": "Imported from PDF via LLM",
            "ingredients": [],
            "instructions": []
        }

        for ing in function_args.get("ingredients", []):
            qty = ing.get("quantity", "")
            unit = ing.get("unit")
            # If unit is present and not already part of quantity string, append it
            if unit and unit.lower() not in qty.lower():
                qty = f"{qty} {unit}"
            
            recipe_data["ingredients"].append({
                "name": ing.get("name"),
                "quantity": qty
            })

        for idx, inst in enumerate(function_args.get("instructions", [])):
            recipe_data["instructions"].append({
                "step_number": idx + 1,
                "text": inst
            })

        return recipe_data

    except OpenAI.AuthenticationError as e:
        error_msg = f"Authentication failed: Invalid API key or expired token"
        print(f"OpenAI AuthenticationError: {e}")
        return {
            "name": "Error: Authentication Failed",
            "description": error_msg,
            "ingredients": [],
            "instructions": []
        }
    
    except OpenAI.RateLimitError as e:
        error_msg = f"Rate limit exceeded. Please try again later."
        print(f"OpenAI RateLimitError: {e}")
        return {
            "name": "Error: Rate Limit Exceeded",
            "description": error_msg,
            "ingredients": [],
            "instructions": []
        }
    
    except OpenAI.BadRequestError as e:
        error_msg = f"Invalid request: {str(e)}"
        print(f"OpenAI BadRequestError: {e}")
        return {
            "name": "Error: Invalid Request",
            "description": error_msg,
            "ingredients": [],
            "instructions": []
        }
    
    except OpenAI.APIConnectionError as e:
        error_msg = f"Failed to connect to OpenAI API. Check network connection."
        print(f"OpenAI APIConnectionError: {e}")
        return {
            "name": "Error: Connection Failed",
            "description": error_msg,
            "ingredients": [],
            "instructions": []
        }
    
    except OpenAI.APITimeoutError as e:
        error_msg = f"Request timed out. The recipe may be too long or complex."
        print(f"OpenAI APITimeoutError: {e}")
        return {
            "name": "Error: Request Timeout",
            "description": error_msg,
            "ingredients": [],
            "instructions": []
        }
    
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        error_msg = f"Failed to parse LLM response: {str(e)}"
        print(f"Response parsing error: {e}")
        return {
            "name": "Error: Invalid LLM Response",
            "description": error_msg,
            "ingredients": [],
            "instructions": []
        }
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"Unexpected error parsing recipe with LLM: {e}")
        return {
            "name": "Error Parsing Recipe",
            "description": error_msg,
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

def suggest_ingredient_duplicates(ingredients: List[str]) -> List[dict]:
    """
    Uses LLM to find potential duplicate ingredients in a list.
    Returns a list of groups, where each group has a 'target' (suggested canonical name)
    and 'sources' (list of variations to merge).
    """
    print(f"[suggest_ingredient_duplicates] Starting with {len(ingredients)} ingredients")
    
    if not ingredients:
        print("[suggest_ingredient_duplicates] No ingredients provided, returning empty list")
        return []

    # Pre-filter: Find potential duplicates using string similarity
    # This reduces the number of ingredients sent to the LLM
    print("[suggest_ingredient_duplicates] Pre-filtering with similarity check...")
    
    from difflib import SequenceMatcher
    
    def similarity(a: str, b: str) -> float:
        """Calculate similarity ratio between two strings (0.0 to 1.0)"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    # Group ingredients that are similar to each other
    SIMILARITY_THRESHOLD = 0.7  # 70% similar
    potential_duplicates = set()
    
    for i, ing1 in enumerate(ingredients):
        for ing2 in ingredients[i+1:]:
            sim = similarity(ing1, ing2)
            if sim >= SIMILARITY_THRESHOLD:
                potential_duplicates.add(ing1)
                potential_duplicates.add(ing2)
    
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
        print(f"[suggest_ingredient_duplicates] Filtered to {len(filtered_ingredients)} potential duplicates (from {len(ingredients)} total)")
    else:
        print("[suggest_ingredient_duplicates] No similar ingredients found, returning empty list")
        return []

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[suggest_ingredient_duplicates] ERROR: No API key provided for duplicate suggestion.")
        return []

    print(f"[suggest_ingredient_duplicates] API key found, initializing OpenAI client")
    client = OpenAI(api_key=api_key)

    prompt = """
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
    
    ingredients_text = json.dumps(filtered_ingredients)
    print(f"[suggest_ingredient_duplicates] Prepared ingredient list, length: {len(ingredients_text)} chars")
    
    try:
        print("[suggest_ingredient_duplicates] Calling OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Here is the list of ingredients:\n{ingredients_text}"}
            ],
            response_format={"type": "json_object"}
        )
        
        print("[suggest_ingredient_duplicates] Received response from OpenAI")
        content = response.choices[0].message.content
        print(f"[suggest_ingredient_duplicates] Response content: {content[:200]}...")
        
        result = json.loads(content)
        print(f"[suggest_ingredient_duplicates] Parsed JSON result, keys: {result.keys()}")
        
        duplicates = result.get("duplicates", [])
        print(f"[suggest_ingredient_duplicates] Found {len(duplicates)} duplicate groups")
        
        return duplicates
        
    except Exception as e:
        print(f"[suggest_ingredient_duplicates] ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []

