from deepdiff import DeepDiff
import json

def compute_diff(before: dict, after: dict):
    dd = DeepDiff(before, after, significant_digits=5, ignore_order=True)
    # Convert to plain JSON-safe dictionary
    def make_json_safe(obj):
        if isinstance(obj, (list, dict, str, int, float, bool)) or obj is None:
            return obj
        try:
            return str(obj)
        except Exception:
            return repr(obj)
    return json.loads(json.dumps(dd, default=make_json_safe))
