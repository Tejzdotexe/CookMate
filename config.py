"""
AI-Powered Smart Recipe Generator
Configuration File
MAEC258 | RVITM MCA | A.Y 2025-2026
"""
import os

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")

class Config:
    SECRET_KEY     = os.environ.get("SECRET_KEY", "rvitm_recipe_ai_2025_secret")
    UPLOAD_FOLDER  = UPLOAD_DIR
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    DEBUG          = True

    # Data file paths
    RECIPES_PATH      = os.path.join(DATA_DIR, "recipes.json")
    SUBSTITUTES_PATH  = os.path.join(DATA_DIR, "substitutes.json")
    NUTRITION_PATH    = os.path.join(DATA_DIR, "nutrition.json")
    TRANSLATIONS_PATH = os.path.join(DATA_DIR, "translations.json")

    # Grocery API base URLs
    BLINKIT_URL = "https://blinkit.com/s/?q="
    ZEPTO_URL   = "https://www.zeptonow.com/search?query="

    # Supported languages
    LANGUAGES = {"en": "English", "hi": "हिंदी", "kn": "ಕನ್ನಡ"}

    # Minimum recipe match threshold (%)
    MIN_MATCH_SCORE = 25
