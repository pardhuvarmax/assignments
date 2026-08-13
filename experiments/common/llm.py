"""
Shared LLM helper used by every experiment in this folder.

All experiments talk to the model exclusively through this module so that
swapping providers or adding an offline fallback only has to happen once.
"""
import os
import sys
import json
import math
import random
from dotenv import load_dotenv
import google.generativeai as genai

# experiments/common/llm.py -> experiments/common -> experiments -> repo root
EXPERIMENTS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(EXPERIMENTS_ROOT)

# Look for a .env in a few plausible spots: the experiments folder itself,
# the repo root, or alongside the older assignment-agenticai project (this
# repo's .env has moved around during reorganization).
_CANDIDATE_ENV_PATHS = [
    os.path.join(EXPERIMENTS_ROOT, ".env"),
    os.path.join(REPO_ROOT, ".env"),
    os.path.join(REPO_ROOT, "assignment-agenticai", ".env"),
]
for _path in _CANDIDATE_ENV_PATHS:
    if os.path.exists(_path):
        load_dotenv(_path)
        break

api_key = os.getenv("GEMINI_API_KEY")

USE_MOCK = False
if not api_key:
    print(f"\n[WARNING] GEMINI_API_KEY not found in {_CANDIDATE_ENV_PATHS}.")
    print("Copy .env.template to .env (in the experiments/ folder) and add your key.")
    print("Running in offline/mock mode for now.\n")
    USE_MOCK = True
else:
    genai.configure(api_key=api_key)

TEXT_MODEL = "gemini-2.5-flash"
EMBED_MODEL = "models/gemini-embedding-001"


def generate_text(prompt: str, system_instruction: str = None) -> str:
    """Plain text completion."""
    global USE_MOCK
    if USE_MOCK:
        return f"[offline-mock reply to: '{prompt[:60]}...']"

    try:
        model = genai.GenerativeModel(model_name=TEXT_MODEL, system_instruction=system_instruction)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            print("\n[WARNING] Gemini quota/rate limit hit. Falling back to offline mock mode.")
            USE_MOCK = True
            return generate_text(prompt, system_instruction)
        print(f"Error during LLM API call: {e}", file=sys.stderr)
        raise


def generate_json(prompt: str, system_instruction: str = None) -> dict:
    """Structured JSON completion. Falls back to a generic stub offline."""
    global USE_MOCK
    if USE_MOCK:
        return {"mock": True, "note": "GEMINI_API_KEY not set; returning a stub JSON object."}

    try:
        model = genai.GenerativeModel(model_name=TEXT_MODEL, system_instruction=system_instruction)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            print("\n[WARNING] Gemini quota/rate limit hit. Falling back to offline mock mode.")
            USE_MOCK = True
            return generate_json(prompt, system_instruction)
        print(f"Error during LLM JSON generation: {e}", file=sys.stderr)
        raise


def describe_image(image_path: str, prompt: str, system_instruction: str = None) -> str:
    """Vision call: answers/describes based on actual image pixels, not a caption."""
    global USE_MOCK
    if USE_MOCK:
        return f"[offline-mock vision reply to: '{prompt[:60]}...']"

    from PIL import Image
    try:
        image = Image.open(image_path)
        model = genai.GenerativeModel(model_name=TEXT_MODEL, system_instruction=system_instruction)
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            print("\n[WARNING] Gemini quota/rate limit hit. Falling back to offline mock mode.")
            USE_MOCK = True
            return describe_image(image_path, prompt, system_instruction)
        print(f"Error during vision LLM call: {e}", file=sys.stderr)
        raise


def get_embedding(text: str) -> list:
    """Embedding vector for retrieval. Deterministic pseudo-vector when offline."""
    if USE_MOCK:
        random.seed(hash(text) % (2**32))
        return [random.uniform(-1, 1) for _ in range(768)]

    try:
        result = genai.embed_content(model=EMBED_MODEL, content=text, task_type="retrieval_document")
        return result["embedding"]
    except Exception as e:
        print(f"Error during embedding generation: {e}", file=sys.stderr)
        raise


def cosine_similarity(v1: list, v2: list) -> float:
    if len(v1) != len(v2):
        raise ValueError("Vectors must be of the same length")
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)
