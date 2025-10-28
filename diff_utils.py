def compute_diff(before: dict, after: dict):
    from deepdiff import DeepDiff
    import json as js
    dd = DeepDiff(before, after, significant_digits=5, ignore_order=True)
    # Convert to plain JSON-safe dictionary
    def make_json_safe(obj):
        if isinstance(obj, (list, dict, str, int, float, bool)) or obj is None:
            return obj
        try:
            return str(obj)
        except Exception:
            return repr(obj)
    return js.loads(js.dumps(dd, default=make_json_safe))
