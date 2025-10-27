import os, json, requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")

class OpenRouterError(Exception):
    pass

def call_openrouter(system_prompt: str, user_payload: dict, model: str = "deepseek/deepseek-r1-0528", timeout=30):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_payload)}
    ]
    payload = {"model": model, "messages": messages, "max_tokens": 1200}

    print(f"[DEBUG] Sending to OpenRouter: {system_prompt[:50]}...")
    print(f"[DEBUG] Payload keys: {list(user_payload.keys())}")

    r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout)
    print(f"[DEBUG] Raw HTTP response text: {r.text[:500]}")
    if not r.ok:
        raise OpenRouterError(f"OpenRouter error {r.status_code}: {r.text}")
    
    try:
        resp = r.json()
        return resp["choices"][0]["message"]["content"]
    except Exception:
        raise RuntimeError(f"Unexpected non-JSON response ({r.status_code}): {r.text[:400]}")