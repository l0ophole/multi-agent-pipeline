import json, copy
from agents import run_agent
from validator import validate_card
from diff_utils import compute_diff

AGENT_SEQUENCE = ["background", "personality", "appearance", "skills", "narrative", "dialogue"]

def normalize_card(card):
    """
    Unifies different card formats so validation and agents can handle them.
    Returns a standardized card with id, name, personality, etc.
    """
    # Case 1: full spec wrapper (like {"spec":"chara_card_v2", "data":{...}})
    if "data" in card:
        card = card["data"]

    # Case 2: analysis-style card (no id, no appearance)
    if "id" not in card:
        # fabricate minimal structure
        normalized = {
            "id": card.get("character_version", "unknown-id"),
            "name": card.get("name", "Unnamed"),
            "appearance": {
                "style": "unspecified",
                "eyes": "unknown",
                "hair": "unknown",
                "height": "unknown"
            },
            "personality": {
                "traits": ["complex", "introspective"],
                "motivations": "unspecified",
                "quips": []
            },
            "background": card.get("description", card.get("scenario", "")),
            "skills": [],
            "dialogue_style": {
                "sentence_length": "medium",
                "vocabulary": "neutral",
                "tone": "neutral"
            },
            "_original": card  # keep reference to raw version if needed
        }
        return normalized

    # Already standard format
    return card


def orchestrate_sync(input_path, output_path, verbose=True):
    with open(input_path) as f:
        card = json.load(f)
    card = normalize_card(card)  # <--- Add this line
    valid, err = validate_card(card)
    if not valid:
        raise ValueError(f"Invalid input: {err}")
    current = card
    change_log = []

    def deep_update(d, u):
        for k, v in u.items():
            if isinstance(v, dict) and isinstance(d.get(k), dict):
                deep_update(d[k], v)
            else:
                d[k] = v

    for agent in AGENT_SEQUENCE:
        before = copy.deepcopy(current)
        try:
            patch = run_agent(agent, current)
        except Exception as e:
            print(f"Agent {agent} failed: {e}")
            continue
        deep_update(current, patch)
        valid, err = validate_card(current)
        if not valid:
            print(f"Agent {agent} produced invalid card: {err}")
            current = before
            change_log.append({"agent": agent, "status": "reverted", "error": err})
            continue
        diff = compute_diff(before, current)

        # change_log.append({"agent": agent, "status": "applied", "diff": diff})
        import json

        try:
            diff_json = json.loads(json.dumps(diff, default=str))
        except Exception:
            diff_json = {"note": "diff not serializable", "raw_type": str(type(diff))}

        change_log.append({"agent": agent, "status": "applied", "diff": diff_json})

        if verbose:
            print(f"Applied {agent}. Diff keys: {list(diff.keys())}")

    with open(output_path, "w") as f:
        json.dump(current, f, indent=2)
    return current, change_log
