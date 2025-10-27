import os, requests
import json as js

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

from config.settings import OPENROUTER_API_KEY

API_KEY = OPENROUTER_API_KEY
# API_MODEL = 'deepseek/deepseek-chat-v3-0324'
# "deepseek/deepseek-r1-0528"
# API_KEY = os.getenv("OPENROUTER_API_KEY")

class OpenRouterError(Exception):
    pass

def call_openrouter(system_prompt: str, user_payload: dict, model: str = 'deepseek/deepseek-chat-v3-0324', timeout=30):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": js.dumps(user_payload)}
    ]
    payload = {"model": model, "messages": messages, "max_tokens": 1200}
    print(f"[DEBUG] user_payload={js.dumps(user_payload, indent=4)}")
    print(f"[DEBUG] payload={js.dumps(payload, indent=4)}")

    print(f"[DEBUG] Sending to OpenRouter: {system_prompt[:50]}...")
    print(f"[DEBUG] Payload keys: {list(user_payload.keys())}")

    r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout)

    raw_response = r.text.strip().rstrip('\n')
    
    ok = r.ok
    status_code = r.status_code
    reason = r.reason
    content = r.content.strip().rstrip('\n')
    text = r.text.strip().rstrip('\n')

    print(f"[RESPONSE] OK: {ok} STATUS_CODE={status_code} REASON={reason} LEN_CONTENT={len(content)} LEN_TEXT={len(text)}")

    print(f"[DEBUG] Raw HTTP response text: {raw_response}")

    print(f"[DEBUG] Raw HTTP response text: {r.text[:500]}")
    
    if not r.ok:
        raise OpenRouterError(f"OpenRouter error {r.status_code}: {r.text}")
    
    try:
        resp = r.json()
        return resp["choices"][0]["message"]["content"]
    except Exception:
        raise RuntimeError(f"Unexpected non-JSON response ({r.status_code}): {r.text[:400]}")