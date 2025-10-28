import os
import requests
import json as js
import dotenv

env_loaded = dotenv.load_dotenv(".env")

if env_loaded is True:
    env_msg = 'env loaded'
else:
    env_msg = 'failed'

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")
DEBUG = os.getenv("DEBUG")

if DEBUG is None:
    DEBUG = False

if DEBUG:
    print(f"DEBUG: load_dotenv('.env'): {env_msg}")

class OpenRouterError(Exception):
    pass

class Requests:
    def __init__(self, logfile=None, debug=False):
        self.logfile = logfile
        self.debug = debug

    def log_post(self, *args, **kwargs):
        p_dict = {'requests_type': 'post',
                  'args': args,
                  'kwargs': kwargs}
        if self.debug is True:
            print(f"[log_post] {js.dumps(p_dict)}")
        if self.logfile is not None:
            with open(self.logfile, 'a') as f:
                f.write(js.dumps(p_dict))

    def log_response(self, r_dict):
        if self.debug is True:
            print(f"[log_response] {js.dumps(r_dict)}")
        if self.logfile is not None:
            with open(self.logfile, 'a') as f:
                f.write(js.dumps(r_dict))

    def post(self, *args, **kwargs):
        r = requests.post(args, kwargs)
        self.log_post(args, kwargs)
        r_dict = {'requests_type': 'response',
                  'ok': r.ok,
                  'status_code': r.status_code,
                  'reason': r.reason,
                  'content': r.content}
        self.log_response(r_dict)

def call_openrouter(system_prompt: str,
                    user_payload: dict,
                    model: str = "deepseek/deepseek-chat-v3-0324",
                    timeout=30):

    if not API_KEY:
        raise OpenRouterError("Missing OPENROUTER_API_KEY environment variable.")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # ✅ DO NOT double-dump JSON
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": js.dumps(user_payload, ensure_ascii=False)},  # pass as dict, not string
    ]

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 1200,
    }
    
    if DEBUG is True:
        print(f"[DEBUG] Authorization header: {headers['Authorization'][:20]}...")  # safe truncation
        print(f"[DEBUG] payload={js.dumps(payload, indent=4)[:500]}")  # optional debug

    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout)

    except Exception as e:
        raise OpenRouterError(f"HTTP request failed: {e}")

    if r.ok is not True:
        raise OpenRouterError(f"OpenRouter returned {r.status_code}: {r.text}")

    try:
        resp = r.json()

    except Exception as e:
        print(f"[DEBUG] Raw HTTP response text: {r.text[:500]}")
        
        raise OpenRouterError(f"Invalid JSON response: {e}")

    try:
        return resp["choices"][0]["message"]["content"]

    except KeyError:
        raise OpenRouterError(f"Malformed response: {resp}")

