# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VibedMeal Planner is a recipe management and meal planning application with AI-powered PDF import. It uses FastAPI (Python) for the backend and React (Vite) for the frontend.

## Development Commands

### Backend (from `backend/` directory)
```bash
# Install dependencies
pip install -r requirements.txt

# Development server with auto-reload (port 8000)
bash start-dev.sh

# Production server with Gunicorn (port 8000)
bash start-gunicorn.sh
```

### Frontend (from `frontend/` directory)
```bash
npm install      # Install dependencies
npm run dev      # Development server (port 5173)
npm run build    # Production build
npm run lint     # ESLint
```

### Docker (from root directory)
```bash
docker-compose up --build  # Backend: 8082, Frontend: 3000
```

### Running Tests
```bash
cd backend && pytest                    # All tests
cd backend && pytest tools/test_*.py    # Test files are in tools/
```

### Linting
```bash
# Frontend
cd frontend && npm run lint

# Backend (pylint configured in .pylintrc)
pylint backend/
```

## Architecture

### Backend Structure
- `main.py` - FastAPI app entry point, CORS config, router registration
- `models.py` - SQLAlchemy models: Recipe, Ingredient, Instruction, MealPlan, ImportTask
- `crud.py` - Database operations
- `services.py` - Business logic including LLM integrations (OpenAI/Gemini)
- `schemas.py` - Pydantic models
- `database.py` - SQLite connection setup
- `routers/` - API endpoints organized by feature

### Frontend Structure
- `src/App.jsx` - Main router setup with React Router
- `src/components/` - React components (RecipeList, Admin, PDFImport, etc.)
- `src/services/api.js` - Axios-based API client with all endpoint wrappers

### Key Data Flow
1. PDF recipes are imported via `/recipes/import/pdf` which creates an `ImportTask`
2. Background processing extracts text with pypdf, then uses LLM (OpenAI or Gemini) to parse structured recipe data
3. The LLM parsing uses a two-stage function-calling approach: first extract raw ingredient lines, then parse the full recipe
4. Recipes are stored with relationships to Ingredients and Instructions
5. Meal plans link to multiple recipes via a many-to-many association table

### LLM Integration
- Located in `services.py`
- Supports both OpenAI (`gpt-4o-mini`) and Gemini (`gemini-2.5-flash-lite`)
- Uses function calling/structured output for reliable parsing
- Ingredient duplicate detection uses Levenshtein pre-filtering before LLM calls

## Environment Variables

Required in `.env` at project root:
- `OPENAI_API_KEY` - For PDF parsing and ingredient analysis
- `GEMINI_API_KEY` - Alternative LLM provider (optional)

Frontend uses `VITE_API_URL` for backend URL (defaults to `http://localhost:8082`).

## Database

SQLite database at `backend/sql_app.db` (also mirrored at root). Schema auto-creates on startup via SQLAlchemy.
