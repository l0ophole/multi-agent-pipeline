from typing import Dict
from openrouter_client import call_openrouter
import json

AGENTS = {
    "background": "You are a writer who improves character backstories. Return only JSON patch updating 'background'. Return only valid JSON with no commentary or explanations.",
    "personality": "You are a personality specialist. Return JSON patch updating 'personality'. Return only valid JSON with no commentary or explanations.",
    "appearance": "Refine appearance descriptions. Output JSON patch for 'appearance'. Return only valid JSON with no commentary or explanations.",
    "skills": "Balance and enhance skills. Output JSON patch for 'skills'. Return only valid JSON with no commentary or explanations.",
    "narrative": "Connect character to story hooks. Output patch with 'story_hooks' or update 'background'. Return only valid JSON with no commentary or explanations.",
    "dialogue": "Modify dialogue_style to match personality. Output patch for 'dialogue_style'. Return only valid JSON with no commentary or explanations."
}

# attempt to solve the empty response from the LLM
updates = [{"appearance": "Refine the appearance details of this character card. Return only a JSON object with the updated 'appearance' key. No extra text."},
           {"skills": "Enhance and balance the 'skills' section. Return only a JSON object containing 'skills'."},
           {"dialogue": "Modify 'dialogue_style' to fit personality. Return only a JSON object with 'dialogue_style'."}]

for d in updates:
    for (k, v) in d.items():
# for (k, v) in updates.items():
        print(f"[update] AGENTS[{k}] = {v}")
        AGENTS[k] = v

import json
from openrouter_client import call_openrouter
import time

def run_agent(agent_key: str, character: dict, retries=2):
    prompt = AGENTS[agent_key]
    for attempt in range(retries + 1):
        try:
            resp_text = call_openrouter(prompt, character)
            if not resp_text.strip():
                raise ValueError("Empty response from OpenRouter.")
            start = resp_text.find("{")
            end = resp_text.rfind("}") + 1
            cleaned = resp_text[start:end]
            return json.loads(cleaned)
        except Exception as e:
            if attempt < retries:
                print(f"[WARN] Agent {agent_key} failed, retrying ({attempt+1}/{retries})...")
                time.sleep(2)
                continue
            raise e
