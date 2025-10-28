from time import sleep


class Agent:
    agent_name: str
    agent_description: str
    max_retries: int
    attempt: int

    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.attempt = 0

    def run(self, character: dict):
        self.attempt = 0
        while self.attempt < self.max_retries:
            self.attempt += 1
            try:
                resp_text = call_openrouter(prompt, character)
                if (resp_text is None) or (not resp_text.strip()):
                    raise ValueError("Empty response from OpenRouter")
                start = resp_text.find('{')
                end = resp_text.rfind('}') + 1
                cleaned = resp_text[start:end]
                patch = js.loads(cleaned)
                return patch
            except Exception as e:
                print(f"[WARN] Agent {self.agent_name} failed, retrying...")
                if self.attempt >= self.max_retries:
                    raise e
                sleep(2)


