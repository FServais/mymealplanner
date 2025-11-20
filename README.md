# 🍽️ VibedMeal Planner

A modern, AI-powered recipe management and meal planning application built with FastAPI and React. Streamline your meal planning, manage recipes, and generate shopping lists with ease.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-18.0+-blue.svg)

## ✨ Features

### 📚 Recipe Management
- **CRUD Operations**: Create, read, update, and delete recipes
- **PDF Import**: Upload PDF recipes and extract content using AI (OpenAI GPT-4)
- **Smart Filtering**: Filter recipes by ingredients with visual search
- **Recipe Thumbnails**: Automatic image caching from Efarmz CDN
- **Bulk Import**: Import multiple PDF recipes concurrently with progress tracking

### 🧠 AI-Powered Tools
- **Ingredient Normalization**: AI-powered duplicate detection and merging
- **Smart Parsing**: Automatic recipe extraction from PDFs with structured output
- **Levenshtein Distance Filtering**: Pre-filters ingredient suggestions to optimize AI token usage

### 🗓️ Meal Planning
- **Meal Plan Builder**: Select recipes and create weekly meal plans
- **Shopping List Generation**: Automatically aggregate ingredients from selected recipes
- **Plan Management**: Save, load, and delete meal plans

### 🛠️ Admin Tools
- **Ingredient Normalizer**: Find and merge duplicate ingredients (e.g., "Tomate" and "Tomates")
- **Manual Merge**: Select specific ingredients to merge without AI assistance
- **Intra-Recipe Duplicate Handling**: Automatically combines quantities when merging creates duplicates

## 🏗️ Tech Stack

### Backend
- **FastAPI**: Modern, fast Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database
- **OpenAI API**: GPT-5-nano for recipe parsing and ingredient analysis
- **Gunicorn + Uvicorn**: Production-grade ASGI server

### Frontend
- **React 18**: Modern UI library
- **React Router**: Client-side routing
- **Lucide React**: Beautiful icon set
- **Vite**: Next-generation frontend tooling

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (optional)
- OpenAI API key

### Installation

#### 1. Clone the repository
```bash
git clone https://github.com/yourusername/my-vibed-meal-planner.git
cd my-vibed-meal-planner
```

#### 2. Set up environment variables
```bash
# Create .env file in the root directory
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here  # Optional
EOF
```

#### 3. Run with Docker (Recommended)
```bash
docker-compose up --build
```

#### 4. Or run locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
# Development mode with auto-reload
bash start-dev.sh
# Or production mode with Gunicorn
bash start-gunicorn.sh
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 🌐 Access the Application
- **Frontend**: http://localhost:5173 (dev) or http://localhost:3000 (Docker)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📖 Usage Guide

### Importing Recipes from PDF
1. Navigate to **Import PDF** page
2. Upload a PDF file containing a recipe
3. AI will automatically extract:
   - Recipe name
   - Description
   - Ingredients with quantities
   - Preparation steps

### Creating a Meal Plan
1. Go to **Recipes** page
2. Select recipes by checking the "Add to Meal Plan" checkbox
3. Navigate to **Meal Plans**
4. Save your meal plan with a name

### Using the Ingredient Normalizer
1. Navigate to **Admin** page
2. Click **Find Duplicates (AI)** to get AI suggestions
3. Review suggested groups and click **Merge**
4. Or use **Manual Merge** to select specific ingredients

### Bulk Import from Efarmz
```bash
# Download recipes from Efarmz
cd tools
python3 efarmz_recipe_downloader.py

# Import all downloaded PDFs
python3 import_recipes.py output/
```

## 🔧 Configuration

### Backend Settings
Edit `backend/database.py` to change database settings:
```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
```

### Frontend API URL
Edit `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Production Server Settings
Edit `backend/start-gunicorn.sh`:
```bash
--workers 4            # Number of worker processes
--worker-class uvicorn.workers.UvicornWorker
--bind 0.0.0.0:8000
```

## 📁 Project Structure

```
my-vibed-meal-planner/
├── backend/
│   ├── routers/           # API endpoints
│   │   ├── recipes.py     # Recipe CRUD
│   │   ├── meal_planner.py # Shopping lists
│   │   ├── meal_plans.py  # Meal plan management
│   │   ├── tools.py       # Admin tools
│   │   └── images.py      # Image caching
│   ├── models.py          # Database models
│   ├── crud.py            # Database operations
│   ├── services.py        # Business logic & AI
│   ├── database.py        # Database connection
│   ├── main.py            # FastAPI app
│   └── data/images/       # Cached thumbnails
├── frontend/
│   └── src/
│       ├── components/    # React components
│       │   ├── RecipeList.jsx
│       │   ├── RecipeForm.jsx
│       │   ├── Admin.jsx
│       │   └── ...
│       └── services/
│           └── api.js     # API client
├── tools/
│   ├── efarmz_recipe_downloader.py
│   ├── import_recipes.py
│   └── normalize_ingredients.py
└── docker-compose.yml
```

## 🔌 API Endpoints

### Recipes
- `GET /recipes/` - List all recipes (with filters)
- `GET /recipes/count` - Count recipes (with filters)
- `GET /recipes/{id}` - Get recipe by ID
- `POST /recipes/` - Create recipe
- `PUT /recipes/{id}` - Update recipe
- `DELETE /recipes/{id}` - Delete recipe
- `POST /recipes/import-pdf` - Import from PDF
- `GET /recipes/ingredients` - Get all unique ingredients

### Meal Planning
- `POST /meal-planner/shopping-list` - Generate shopping list
- `GET /meal-plans/` - List all meal plans
- `POST /meal-plans/` - Create meal plan
- `DELETE /meal-plans/{id}` - Delete meal plan

### Admin Tools
- `POST /tools/ingredients/suggest-duplicates` - AI duplicate detection
- `POST /tools/ingredients/merge` - Merge ingredients

### Images
- `GET /images/thumbnails/{filename}` - Get cached thumbnail

## 🛠️ Development

### Running Tests
```bash
cd backend
pytest
```

### Database Migrations
```bash
# Add new column (example)
python tools/add_source_file_column.py
```

### Code Style
```bash
# Backend
black backend/
flake8 backend/

# Frontend
npm run lint
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4 |
| `GEMINI_API_KEY` | No | Google Gemini API key (alternative) |

## 🐛 Troubleshooting

### Backend returns 503 during bulk import
Increase concurrency limit in `backend/start-dev.sh`:
```bash
--limit-concurrency 50
```

### Images not loading
Check that `backend/data/images/` directory exists and is writable.

### Frontend can't connect to backend
Verify CORS settings in `backend/main.py` and API URL in frontend.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Recipe images courtesy of [Efarmz](https://efarmz.be)
- Icons by [Lucide](https://lucide.dev)
- AI powered by [OpenAI](https://openai.com)

## 📧 Contact

Project Link: [https://github.com/yourusername/my-vibed-meal-planner](https://github.com/yourusername/my-vibed-meal-planner)

---

**Built with ❤️ using FastAPI & React**
