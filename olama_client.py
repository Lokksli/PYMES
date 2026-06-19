"""Simple local Ollama HTTP client wrapper."""
import json
from typing import Optional, Dict
import os

OLAMA_URL = os.environ.get('OLAMA_URL', 'http://127.0.0.1:11434/api/generate')


def analyze_message_with_olama(message: str, timeout: float = 10.0) -> Optional[Dict]:
    if not message:
        return None

    try:
        import requests
    except Exception:
        return None

    prompt = (
        "You are a content moderation assistant. "
        "Analyze the message for bad words, hate speech, harassment, or explicit content. But moderate only if it's clearly inappropriate. If the message is borderline or ambiguous, do not ban. Also just badwords without hate speech is acceptable\n\n"
        "Output ONLY a valid JSON object with these exact keys:\n"
        '  "ban": true or false\n'
        '  "reason": short string explaining why (or empty string)\n'
        '  "confidence": float between 0.0 and 1.0\n\n'
        "No markdown, no explanation, just the JSON object.\n\n"
        f"Message: {message}\n\nJSON:"
    )

    payload = {
        'model': os.environ.get('OLAMA_MODEL', 'llama3'),  # FIX 2: correct default model name
        'prompt': prompt,
        'num_predict': 200,   # FIX 3: Ollama uses num_predict, not max_tokens
        'temperature': 0.0,
        'stream': False,      # FIX 4: disable streaming for clean single JSON response
    }

    try:
        r = requests.post(OLAMA_URL, json=payload, timeout=timeout)
        r.raise_for_status()

        data = r.json()
        # With stream=False, Ollama returns a single object with a 'response' key
        out = data.get('response', '').strip()

        if not out:
            return None

        # Try direct parse first
        try:
            return json.loads(out)
        except Exception:
            # Fallback: extract first {...} substring
            start = out.find('{')
            end = out.rfind('}')
            if start != -1 and end > start:
                try:
                    return json.loads(out[start:end + 1])
                except Exception:
                    return None
            return None

    except Exception as e:
        print(f"[Ollama] Request failed: {type(e).__name__}: {e}")
        return None