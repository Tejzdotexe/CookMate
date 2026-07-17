"""
AI Feature: NLP Recipe Matching Engine
Uses tokenization, lemmatization and fuzzy string matching
to score and rank recipes by ingredient overlap.
MAEC258 | RVITM MCA | A.Y 2025-2026
"""
import json, re
from difflib import SequenceMatcher


# ── Common pantry/spice items that should NOT count against match score ──────
PANTRY_ITEMS = {
    # Spices & seasonings
    "salt","pepper","black pepper","white pepper","turmeric","cumin","cumin seeds",
    "coriander powder","coriander seeds","red chilli powder","chilli powder",
    "garam masala","biryani masala","chana masala","chole masala","pav bhaji masala",
    "sambar powder","rasam powder","kitchen king","curry powder","mustard seeds",
    "fenugreek seeds","methi seeds","asafoetida","hing","bay leaf","bay leaves",
    "cardamom","cloves","cinnamon","star anise","whole spices","dried red chilli",
    "kasuri methi","dried fenugreek","ajwain","carom seeds","nigella seeds","kalonji",
    "saffron","nutmeg","mace","fennel seeds","poppy seeds",
    # Liquids & oils
    "oil","water","ghee","butter","cooking oil","sunflower oil","vegetable oil",
    # Leavening & thickeners
    "baking soda","baking powder","cornflour","cornstarch","arrowroot",
    # Aromatics (small quantities used as seasoning)
    "curry leaves","kadi patta",
    # Common garnishes
    "coriander leaves","cilantro","mint leaves","spring onion",
    # Sugar & sweeteners
    "sugar","jaggery","honey","rose water","kewra water",
    # Acids
    "lemon juice","lime juice","vinegar","tamarind",
    # Misc
    "salt to taste","to taste","as needed","pinch","handful",
    "whole spices","mixed spices",
}


class RecipeMatcher:
    def __init__(self, recipes_path: str):
        with open(recipes_path, "r", encoding="utf-8") as f:
            self.recipes = json.load(f)
        self._all_ingredients = self._build_ingredient_index()

    # ── Private Helpers ─────────────────────────────────────────────────────
    def _normalize(self, text: str) -> str:
        """Lowercase, strip punctuation, remove filler words."""
        text  = text.lower().strip()
        text  = re.sub(r"[^a-z0-9 ]", "", text)
        stops = {"a","an","the","of","with","and","some","fresh","dried",
                 "large","medium","small","to","taste","as","needed",
                 "pinch","handful","ripe","boneless","skinless"}
        words = [w for w in text.split() if w not in stops]
        return " ".join(words).strip()

    def _similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    def _is_pantry(self, ingredient_name: str) -> bool:
        """Return True if ingredient is a common pantry/spice item."""
        n = ingredient_name.lower().strip()
        # Exact match
        if n in PANTRY_ITEMS:
            return True
        # Partial match - if any pantry word is in the ingredient name
        for p in PANTRY_ITEMS:
            if p in n:
                return True
        return False

    def _ingredient_match(self, user_ings: list, recipe_ings: list):
        """
        Score recipe based on how many KEY ingredients the user has.
        Pantry items (spices, salt, oil) are excluded from scoring.
        """
        user_norm = [self._normalize(i) for i in user_ings]

        # Separate KEY ingredients from PANTRY items
        key_ings    = [r for r in recipe_ings if not self._is_pantry(r["name"])]
        pantry_ings = [r for r in recipe_ings if self._is_pantry(r["name"])]

        # If no key ingredients found, use all ingredients
        if not key_ings:
            key_ings = recipe_ings

        matched = []
        missing = []

        for r_obj in key_ings:
            r_name = self._normalize(r_obj["name"])
            found  = False
            for u_ing in user_norm:
                if (u_ing in r_name or
                        r_name in u_ing or
                        self._similarity(u_ing, r_name) > 0.70):
                    matched.append(r_obj["name"])
                    found = True
                    break
            if not found:
                missing.append(r_obj["name"])

        total = len(key_ings)
        score = round((len(matched) / total) * 100) if total else 0

        # Also check pantry items user has (bonus, doesn't reduce score)
        pantry_matched = []
        for r_obj in pantry_ings:
            r_name = self._normalize(r_obj["name"])
            for u_ing in user_norm:
                if u_ing in r_name or r_name in u_ing:
                    pantry_matched.append(r_obj["name"])
                    break

        return score, matched, missing, pantry_matched

    def _build_ingredient_index(self) -> list:
        ings = set()
        for r in self.recipes:
            for i in r.get("ingredients_list", []):
                ings.add(i["name"].lower())
        return sorted(list(ings))

    # ── Public Methods ──────────────────────────────────────────────────────
    def match(self, user_ingredients: list, diet_filter: str = "all") -> list:
        """
        Match user ingredients against all recipes.
        Returns list sorted by match score (best first).
        """
        if not user_ingredients:
            return []

        results = []
        for recipe in self.recipes:
            # Diet filter
            if diet_filter != "all" and recipe.get("diet") != diet_filter:
                continue

            score, matched, missing, pantry = self._ingredient_match(
                user_ingredients, recipe.get("ingredients_list", [])
            )

            # Lower threshold — show recipes with at least 1 key ingredient match
            # OR if user has at least 20% of key ingredients
            if score >= 20 or len(matched) >= 1:
                r = dict(recipe)
                r["match_score"]          = score
                r["matched_ingredients"]  = matched
                r["missing_ingredients"]  = missing
                r["pantry_matched"]       = pantry
                results.append(r)

        # Sort: first by match_score, then by rating
        results.sort(key=lambda x: (x["match_score"], x.get("rating", 0)), reverse=True)
        return results[:10]

    def get_by_id(self, recipe_id: int) -> dict:
        for r in self.recipes:
            if r["id"] == recipe_id:
                return dict(r)
        return None

    def get_all_ingredients(self) -> list:
        return self._all_ingredients

    def get_all(self) -> list:
        return self.recipes
