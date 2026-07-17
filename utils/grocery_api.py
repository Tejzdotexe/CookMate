"""grocery_api.py — Feature 6: Blinkit / Zepto Grocery API Integration"""
import urllib.parse, random

class GroceryAPI:
    def __init__(self, blinkit_url: str, zepto_url: str):
        self.blinkit = blinkit_url
        self.zepto   = zepto_url

    def _enc(self, t): return urllib.parse.quote(t)
    def _eta(self):    return f"{random.randint(8,18)} minutes"

    def get_links(self, ingredients: list) -> dict:
        return {i: {"blinkit": self.blinkit+self._enc(i),
                    "zepto":   self.zepto+self._enc(i),
                    "eta":     self._eta()} for i in ingredients}

    def place_order(self, ingredients: list, platform="blinkit") -> dict:
        if not ingredients:
            return {"status":"error","message":"No ingredients provided"}
        q   = " ".join(ingredients[:3])
        url = (self.blinkit if platform=="blinkit" else self.zepto) + self._enc(q)
        return {"status":"success","platform":platform.capitalize(),
                "items":ingredients,"order_url":url,"eta":self._eta(),
                "message":f"Redirecting to {platform.capitalize()} for {len(ingredients)} item(s)"}
