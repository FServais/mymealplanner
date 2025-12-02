from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import models
from database import engine
from routers import recipes, meal_planner, meal_plans, tools, images

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
logger.info("Starting Recipe Manager API")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recipe Manager API")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "*", # For development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipes.router)
app.include_router(meal_planner.router)
app.include_router(tools.router)
app.include_router(images.router)
app.include_router(tools.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Recipe Manager API"}
