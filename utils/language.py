"""language.py — Feature 7: Multi-Language Translator"""
import json

class Translator:
    def __init__(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
    def get(self, lang="en") -> dict:
        return self.data.get(lang, self.data["en"])
