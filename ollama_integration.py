"""
Ollama REST Integration Layer for Gemini Prompt Builder
--------------------------------------------------------
Handles:
- Model discovery via REST or local list()
- Prompt enhancement calls to Ollama REST API
- JSON-safe communication for Streamlit integration
"""

import requests
import json
import ollama
from typing import List, Dict, Tuple

OLLAMA_BASE = "http://127.0.0.1:11434"


# ---------- MODEL DISCOVERY ----------

def get_available_models() -> List[str]:
    """Fetch all installed Ollama models via REST first, fallback to local client."""
    # 1. REST call
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            if models:
                return sorted(models)
    except Exception:
        pass

    # 2. Fallback via Python client
    try:
        local = ollama.list()
        return sorted([m["name"] for m in local.get("models", [])])
    except Exception:
        return []


# ---------- PROMPT ENHANCEMENT ----------

def enhance_prompt(prompt: str, model: str, mode: str = "creative") -> Tuple[str, bool]:
    """
    Send enhancement request to Ollama REST API.

    Args:
        prompt: Base prompt string to enhance.
        model: Model name (e.g., deepseek-r1:8b).
        mode: Enhancement mode ('strict' or 'creative').

    Returns:
        (enhanced_prompt, success_flag)
    """
    if not model:
        return prompt, False

    if mode == "strict":
        task = (
            "Rewrite the following prompt for clarity, grammar, and readability, "
            "without altering any factual or technical details. "
            "Preserve all realism and lighting instructions."
        )
    else:
        task = (
            "Rewrite the following prompt in a cinematic and emotionally rich style, "
            "keeping all photographic and realism specifications intact. "
            "Enhance flow and immersion."
        )

    payload = {
        "model": model,
        "prompt": f"{task}\n\nPrompt:\n{prompt}\n\nEnhanced version:",
        "stream": False,
        "options": {"temperature": 0.6, "num_predict": 400}
    }

    try:
        r = requests.post(f"{OLLAMA_BASE}/api/generate", json=payload, timeout=60)
        if r.ok:
            response = r.json().get("response", "").strip()
            if response:
                return response, True
    except Exception:
        pass

    return prompt, False


# ---------- MODEL STATUS CHECK ----------

def get_server_status() -> Dict[str, str]:
    """Return basic server health info for diagnostics."""
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return {
                "status": "online",
                "models_detected": len(data.get("models", [])),
                "model_names": [m["name"] for m in data.get("models", [])]
            }
        else:
            return {"status": "unreachable", "models_detected": 0, "model_names": []}
    except Exception as e:
        return {"status": f"error: {str(e)}", "models_detected": 0, "model_names": []}
