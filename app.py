"""
AI-Powered Smart Recipe Generator
Main Flask Application
Author: RVITM MCA Student | MAEC258 | A.Y 2025-2026

Features:
  1. CNN Ingredient Image Detection
  2. NLP Substitute Ingredient Suggester
  3. Calorie & Nutrition Estimator (Linear Regression)
  4. Voice-Based Ingredient Input (Speech Recognition)
  5. Personalised Recipe Recommender (Content-Based Filtering)
  6. Blinkit / Zepto Grocery API Integration
  7. Multi-Language Support (English, Hindi, Kannada)
"""

import os
import json
import logging
from flask import (Flask, render_template, request,
                   jsonify, session, redirect, url_for, flash)
from werkzeug.utils import secure_filename
from config import Config

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── App Initialisation ──────────────────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ── Context Processor — inject into ALL templates automatically ─────────────────
@app.context_processor
def inject_globals():
    """Makes 'languages' and 'lang' available in every template automatically."""
    lang = session.get("lang", "en")
    return dict(
        languages=app.config["LANGUAGES"],
        lang=lang
    )

# ── Import AI/ML Modules ────────────────────────────────────────────────────────
from models.recipe_matcher       import RecipeMatcher
from models.substitute_suggester import SubstituteSuggester
from models.calorie_estimator    import CalorieEstimator
from models.recipe_recommender   import RecipeRecommender
from models.ingredient_detector  import IngredientDetector
from utils.language              import Translator
from utils.grocery_api           import GroceryAPI

# ── Initialise AI components (loaded once at startup) ───────────────────────────
logger.info("Loading AI/ML components...")
matcher    = RecipeMatcher(app.config["RECIPES_PATH"])
substitute = SubstituteSuggester(app.config["SUBSTITUTES_PATH"])
calorie    = CalorieEstimator(app.config["NUTRITION_PATH"])
recommender= RecipeRecommender(app.config["RECIPES_PATH"])
detector   = IngredientDetector()
translator = Translator(app.config["TRANSLATIONS_PATH"])
grocery    = GroceryAPI(app.config["BLINKIT_URL"], app.config["ZEPTO_URL"])
logger.info("All AI/ML components loaded successfully.")

# ── Helpers ─────────────────────────────────────────────────────────────────────
def allowed_file(filename):
    return ("." in filename and
            filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"])

def get_lang():
    return session.get("lang", "en")

def parse_ingredients(raw: str) -> list:
    """Parse comma/newline separated ingredient string into clean list."""
    items = []
    for part in raw.replace(",", "\n").split("\n"):
        item = part.strip().lower()
        if item and len(item) > 1:
            items.append(item)
    return list(dict.fromkeys(items))   # deduplicate preserving order

# ── Routes ───────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Home page with search form and personalised recommendations."""
    lang        = get_lang()
    t           = translator.get(lang)
    history     = session.get("history", [])
    recommended = recommender.recommend(history, n=4)
    popular     = recommender.get_popular(n=8)
    return render_template("index.html",
                           t=t,
                           recommended=recommended,
                           popular=popular)


@app.route("/search", methods=["POST"])
def search():
    """Search recipes by typed ingredient list with optional diet filter."""
    lang        = get_lang()
    t           = translator.get(lang)
    raw         = request.form.get("ingredients", "").strip()
    diet        = request.form.get("diet", "all")
    ing_list    = parse_ingredients(raw)

    if not ing_list:
        flash("Please enter at least one ingredient.", "warning")
        return redirect(url_for("index"))

    recipes = matcher.match(ing_list, diet_filter=diet)
    for r in recipes:
        r["calorie_info"] = calorie.estimate(
            r.get("ingredients_list", []), r.get("servings", 4)
        )

    return render_template("results.html",
                           recipes=recipes,
                           ingredients=ing_list,
                           diet=diet,
                           t=t,
                           query=", ".join(ing_list))


@app.route("/recipe/<int:recipe_id>")
def recipe_detail(recipe_id):
    """Full recipe detail page with nutrition, substitutes, and grocery links."""
    lang   = get_lang()
    t      = translator.get(lang)
    recipe = matcher.get_by_id(recipe_id)

    if not recipe:
        flash("Recipe not found.", "danger")
        return redirect(url_for("index"))

    history = session.get("history", [])
    if recipe_id not in history:
        history.append(recipe_id)
    session["history"] = history[-30:]

    calorie_info     = calorie.estimate(
        recipe.get("ingredients_list", []), recipe.get("servings", 4)
    )
    ingredient_names = [i["name"] for i in recipe.get("ingredients_list", [])]
    substitutes      = {ing: substitute.suggest(ing) for ing in ingredient_names}
    grocery_links    = grocery.get_links(ingredient_names[:6])
    similar_recipes  = recommender.similar(recipe_id, n=4)

    return render_template("recipe_detail.html",
                           recipe=recipe,
                           calorie_info=calorie_info,
                           substitutes=substitutes,
                           grocery_links=grocery_links,
                           similar=similar_recipes,
                           t=t)


# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.route("/api/detect", methods=["POST"])
def api_detect():
    """
    AI Feature 1: CNN Ingredient Image Detection
    Accepts an uploaded image and returns detected ingredient list.
    """
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image provided"}), 400

    file = request.files["image"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Invalid file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        detections  = detector.detect_with_confidence(filepath)
        ingredients = [d["ingredient"] for d in detections]
        return jsonify({
            "success":     True,
            "ingredients": ingredients,
            "detections":  detections,
            "message":     f"Detected {len(ingredients)} ingredients"
        })
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except Exception:
            pass


@app.route("/api/voice", methods=["POST"])
def api_voice():
    """
    AI Feature 4: Voice-Based Ingredient Input
    Activates microphone, captures speech, returns ingredient list.
    """
    lang = get_lang()
    try:
        from models.voice_input import VoiceInput
        vi          = VoiceInput()
        raw_text    = vi.listen(lang=lang)
        ingredients = vi.process_text(raw_text)
        return jsonify({
            "success":     True,
            "ingredients": ingredients,
            "raw_text":    raw_text
        })
    except ImportError:
        return jsonify({
            "success": False,
            "error":   "SpeechRecognition library not installed. Run: pip install SpeechRecognition pyaudio"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 200


@app.route("/api/substitute/<path:ingredient>")
def api_substitute(ingredient):
    """
    AI Feature 2: Smart Substitute Ingredient Suggester
    Returns substitute suggestions for a given ingredient.
    """
    result = substitute.suggest(ingredient)
    return jsonify(result)


@app.route("/api/nutrition", methods=["POST"])
def api_nutrition():
    """
    AI Feature 3: Calorie & Nutrition Estimator
    Accepts ingredient list JSON and returns nutritional breakdown.
    """
    data       = request.get_json()
    ingredients= data.get("ingredients", [])
    servings   = data.get("servings", 4)
    result     = calorie.estimate(ingredients, servings)
    return jsonify(result)


@app.route("/api/order", methods=["POST"])
def api_order():
    """
    Feature 6: Grocery API — Blinkit / Zepto Integration
    Returns order links for missing ingredients.
    """
    data        = request.get_json() or {}
    ingredients = data.get("ingredients", [])
    platform    = data.get("platform", "blinkit")
    result      = grocery.place_order(ingredients, platform)
    return jsonify(result)


@app.route("/api/recommend")
def api_recommend():
    """
    AI Feature 5: Personalised Recipe Recommender
    Returns recommendations based on session history.
    """
    history     = session.get("history", [])
    recommended = recommender.recommend(history, n=6)
    return jsonify({"recipes": recommended})


@app.route("/lang/<code>")
def set_lang(code):
    """
    Feature 7: Multi-Language Support
    Sets session language to English (en), Hindi (hi), or Kannada (kn).
    """
    if code in app.config["LANGUAGES"]:
        session["lang"] = code
        logger.info(f"Language set to: {code}")
    return redirect(request.referrer or url_for("index"))


@app.route("/api/search_ajax", methods=["POST"])
def search_ajax():
    """AJAX endpoint for live ingredient search suggestions."""
    query    = request.get_json().get("query", "").lower()
    all_ings = matcher.get_all_ingredients()
    matches  = [i for i in all_ings if query in i][:10]
    return jsonify({"suggestions": matches})


# ── Error Handlers ───────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    t = translator.get(session.get("lang", "en"))
    return render_template("index.html",
                           t=t,
                           recommended=[],
                           popular=[],
                           error="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return jsonify({"error": "Internal server error"}), 500


# ── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting AI-Powered Smart Recipe Generator...")
    logger.info("Open http://localhost:5000 in your browser")
    app.run(debug=True, host="0.0.0.0", port=5000)
