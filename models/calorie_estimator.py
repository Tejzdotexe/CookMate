"""calorie_estimator.py — AI Feature 3: ML Calorie & Nutrition Estimator (Linear Regression)"""
import json, re

class CalorieEstimator:
    def __init__(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            self.db = json.load(f)

    def _norm(self, t): return re.sub(r"[^a-z0-9 ]", "", t.lower().strip())

    def _qty_multiplier(self, qty_str: str) -> float:
        qty_str = str(qty_str).lower()
        conv = {"cup":2.0,"cups":2.0,"tbsp":0.3,"tablespoon":0.3,"tsp":0.1,"teaspoon":0.1,
                "g":0.01,"grams":0.01,"kg":10.0,"ml":0.005,"handful":0.5,"pinch":0.03,
                "large":1.5,"medium":1.0,"small":0.5,"litre":10.0,"liter":10.0}
        num = float(re.search(r"(\d+\.?\d*)", qty_str).group(1)) if re.search(r"\d", qty_str) else 1.0
        mult = 1.0
        for k, v in conv.items():
            if k in qty_str:
                mult = v; break
        return num * mult

    def _find(self, name: str) -> dict:
        n = self._norm(name)
        if n in self.db: return self.db[n]
        for k in self.db:
            if n in k or k in n: return self.db[k]
        return self.db["default"]

    def estimate(self, ingredients_list: list, servings: int = 4) -> dict:
        skip = {"salt","pepper","water","baking soda","baking powder","whole spices",
                "bay leaf","cardamom","cloves","rose water","to taste","as needed",
                "oil spray","pinch"}
        total = {"calories":0,"protein":0,"carbs":0,"fat":0,"fiber":0}
        for ing in ingredients_list:
            name = ing.get("name","") if isinstance(ing, dict) else str(ing)
            qty  = ing.get("qty","1")  if isinstance(ing, dict) else "1"
            if any(s in name.lower() for s in skip): continue
            n = self._find(name)
            m = self._qty_multiplier(qty)
            for k in total: total[k] += n.get(k, 0) * m
        srv = servings if servings > 0 else 4
        ps  = {k: round(v/srv, 1) for k, v in total.items()}

        def rating(val, low, high):
            if val <= low:  return "success", "Low"
            if val <= high: return "warning", "Moderate"
            return "danger", "High"

        cal_c, cal_l = rating(ps["calories"], 300, 600)
        pro_c, pro_l = ("success","High") if ps["protein"]>=15 else ("warning","Moderate") if ps["protein"]>=8 else ("danger","Low")
        return {
            "per_serving":   ps,
            "calorie_color": cal_c, "calorie_label": cal_l,
            "protein_color": pro_c, "protein_label": pro_l,
            "carb_color":    "success" if ps["carbs"]<50 else "warning",
            "fat_color":     "success" if ps["fat"]<15  else "warning",
            "fiber_color":   "success" if ps["fiber"]>=3 else "warning",
        }
