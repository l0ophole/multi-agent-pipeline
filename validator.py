import jsonschema
import json as js

def load_schema(path="schema.json"):
    with open(path) as f:
        return js.load(f)

schema = load_schema()

def validate_card(card: dict):
    required_keys = {"id", "name", "personality"}
    if not required_keys.issubset(set(card.keys())):
        return False, f"Missing required keys: {required_keys - set(card.keys())}"
    return True, None
