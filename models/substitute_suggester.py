"""substitute_suggester.py — AI Feature 2: NLP Ingredient Substitute Suggester"""
import json, re
from difflib import get_close_matches

class SubstituteSuggester:
    def __init__(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            self.kb = json.load(f)
        self.keys = list(self.kb.keys())

    def _norm(self, t): return re.sub(r"[^a-z0-9 \-]", "", t.lower().strip())

    def suggest(self, ingredient: str) -> dict:
        n = self._norm(ingredient)
        if n in self.kb:
            return {"ingredient": ingredient, "substitutes": self.kb[n], "found": True}
        for k in self.keys:
            if n in k or k in n:
                return {"ingredient": ingredient, "substitutes": self.kb[k], "found": True}
        matches = get_close_matches(n, self.keys, n=1, cutoff=0.6)
        if matches:
            return {"ingredient": ingredient, "substitutes": self.kb[matches[0]], "found": True}
        return {"ingredient": ingredient,
                "substitutes": [{"substitute": "Ask at local grocery store",
                                  "ratio": "Staff can suggest best local alternative",
                                  "use_for": "general cooking"}],
                "found": False}
