"""
Indexing step for the visual retrieval pipeline: since text-embedding
models don't take images, each image is first captioned by the vision
model (one call per image), then the CAPTION is embedded for retrieval.
This is a standard practical pattern for image search without a dedicated
image-embedding model. The caption is deliberately coarse (topic-level),
so retrieval finds the right image, but visual_qa.py still has to look at
actual pixels for anything precise (counts, colors, which light is lit).
"""
import os
import sys
import json
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(HERE, "images")
INDEX_PATH = os.path.join(HERE, "visual_index.json")

CAPTION_PROMPT = (
    "Describe this image in one sentence for a search index: its general "
    "subject/topic only (e.g. 'a bar chart of quarterly revenue', 'a "
    "network diagram'). Do not enumerate exact counts, colors, or labels."
)


def _fingerprint() -> str:
    h = hashlib.sha256()
    for name in sorted(os.listdir(IMAGES_DIR)):
        path = os.path.join(IMAGES_DIR, name)
        if os.path.isfile(path):
            h.update(name.encode())
            h.update(open(path, "rb").read())
    return h.hexdigest()


def _build_index() -> dict:
    print("[indexer] Captioning images (one vision call per image)...")
    entries = {}
    for name in sorted(os.listdir(IMAGES_DIR)):
        path = os.path.join(IMAGES_DIR, name)
        if not os.path.isfile(path):
            continue
        caption = llm.describe_image(path, CAPTION_PROMPT)
        print(f"  {name}: {caption.strip()}")
        entries[name] = {"caption": caption, "embedding": llm.get_embedding(caption)}

    with open(INDEX_PATH, "w") as f:
        json.dump({"fingerprint": _fingerprint(), "entries": entries}, f)
    return entries


def load_or_build_index() -> dict:
    if os.path.exists(INDEX_PATH):
        cached = json.load(open(INDEX_PATH))
        if cached.get("fingerprint") == _fingerprint():
            return cached["entries"]
        print("[indexer] images/ changed since last index; rebuilding.")
    return _build_index()


if __name__ == "__main__":
    entries = _build_index()
    print(f"Indexed {len(entries)} images.")
