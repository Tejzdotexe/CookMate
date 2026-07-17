# AI-Powered Smart Recipe Generator


---

## 7 AI / ML Features
| # | Feature | Technology |
|---|---------|-----------|
| 1 | Ingredient Image Detection | CNN + TensorFlow + MobileNet |
| 2 | Substitute Ingredient Suggester | NLP + NLTK Knowledge Base |
| 3 | Calorie & Nutrition Estimator | Linear Regression + Scikit-learn |
| 4 | Voice-Based Ingredient Input | SpeechRecognition + PyAudio |
| 5 | Personalised Recipe Recommender | Content-Based Filtering |
| 6 | Grocery Ordering (Blinkit/Zepto) | REST API Integration |
| 7 | Multi-Language Support | Flask-i18n (English, Hindi, Kannada) |

---

## Quick Start

### 1. Install Dependencies
```bash
pip install flask nltk scikit-learn numpy Pillow SpeechRecognition werkzeug
# Optional (for CNN and voice):
pip install tensorflow opencv-python-headless pyaudio
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
```
http://localhost:5000
```

---

## Project Structure
```
AI_Recipe_Generator_PRO/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── models/
│   ├── recipe_matcher.py   # NLP recipe matching
│   ├── substitute_suggester.py
│   ├── calorie_estimator.py
│   ├── recipe_recommender.py
│   ├── ingredient_detector.py  # CNN image detection
│   └── voice_input.py      # Speech recognition
├── data/
│   ├── recipes.json        # 20 Indian recipes
│   ├── substitutes.json    # 25+ ingredient substitutes
│   ├── nutrition.json      # USDA nutrition data
│   └── translations.json   # EN / HI / KN translations
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── results.html
│   └── recipe_detail.html
├── static/
│   ├── css/style.css
│   └── js/main.js
└── utils/
    ├── language.py
    └── grocery_api.py
```
