import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import services

router = APIRouter(
    prefix="/tools/pdf",
    tags=["pdf-review"],
)

# Directory for storing uploaded PDFs
PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pdfs")

# Ensure directory exists
os.makedirs(PDF_DIR, exist_ok=True)


class RawIngredientLine(BaseModel):
    raw_text: str
    serving_hint: Optional[str] = None


class PDFExtractResponse(BaseModel):
    raw_text: str
    raw_lines: List[RawIngredientLine]


@router.post("/upload")
async def upload_pdf_for_review(file: UploadFile = File(...)):
    """
    Upload a PDF for bulk review. Stores it in data/pdfs/ directory.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    content = await file.read()

    # Save to data/pdfs/{original_filename}
    file_path = os.path.join(PDF_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": file.filename,
        "size": len(content),
        "stored": True
    }


@router.get("/{filename}")
async def get_pdf(filename: str):
    """
    Serve a stored PDF file for display in the browser.
    """
    file_path = os.path.join(PDF_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename
    )


@router.get("/list/all")
async def list_pdfs():
    """
    List all stored PDFs available for review.
    """
    if not os.path.exists(PDF_DIR):
        return []

    files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
    return sorted(files)


@router.post("/extract-text", response_model=PDFExtractResponse)
async def extract_text_from_pdf(
    file: UploadFile = File(...),
    provider: str = Query("gemini", description="LLM provider: 'openai' or 'gemini'")
):
    """
    Extract raw text and ingredient lines from a PDF without creating a recipe.
    Useful for reviewing what was detected vs what ended up in the recipe.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    content = await file.read()

    # Extract raw text
    raw_text = services.extract_text_from_pdf(content)
    if not raw_text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # Extract raw ingredient lines using Stage 1 LLM
    result = services.extract_raw_ingredients_only(raw_text, provider=provider)

    return PDFExtractResponse(
        raw_text=raw_text,
        raw_lines=[RawIngredientLine(**line) for line in result.get("raw_lines", [])]
    )


@router.delete("/{filename}")
async def delete_pdf(filename: str):
    """
    Delete a stored PDF file.
    """
    file_path = os.path.join(PDF_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found")

    os.remove(file_path)
    return {"deleted": True, "filename": filename}
