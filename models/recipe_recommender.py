"""recipe_recommender.py — AI Feature 5: Content-Based Filtering Recommender"""
import json

class RecipeRecommender:
    def __init__(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            self.recipes = json.load(f)

    def _tags(self, r):
        t = r.get("tags", []) + [r.get("cuisine",""), r.get("diet",""), r.get("difficulty","")]
        return [x.lower() for x in t if x]

    def recommend(self, history_ids: list, n: int = 4) -> list:
        if not history_ids:
            return sorted(self.recipes, key=lambda r: r.get("rating",0), reverse=True)[:n]
        liked = []
        for rid in history_ids:
            for r in self.recipes:
                if r["id"] == rid: liked.extend(self._tags(r))
        scored = []
        for r in self.recipes:
            if r["id"] in history_ids: continue
            score = sum(1 for t in self._tags(r) if t in liked)
            scored.append((score, r))
        scored.sort(key=lambda x: (x[0], x[1].get("rating",0)), reverse=True)
        return [r for _, r in scored[:n]]

    def similar(self, recipe_id: int, n: int = 4) -> list:
        base = next((r for r in self.recipes if r["id"]==recipe_id), None)
        if not base: return self.get_popular(n)
        base_tags = self._tags(base)
        scored = [(sum(1 for t in self._tags(r) if t in base_tags), r)
                  for r in self.recipes if r["id"] != recipe_id]
        scored.sort(key=lambda x: (x[0], x[1].get("rating",0)), reverse=True)
        return [r for _, r in scored[:n]]

    def get_popular(self, n: int = 8) -> list:
        return sorted(self.recipes, key=lambda r: (r.get("views",0), r.get("rating",0)), reverse=True)[:n]
