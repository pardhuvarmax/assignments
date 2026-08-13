"""
Retrieval over the source memos for the deep research agent. Each file in
sources/ is short enough (one internal memo) to embed as a single chunk --
this experiment is about the planning/reflection loop on top of retrieval,
not chunking strategy (see experiment 2 for that).
"""
import os
import sys
import json
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES_DIR = os.path.join(HERE, "sources")
INDEX_PATH = os.path.join(HERE, "sources_index.json")


def _fingerprint() -> str:
    h = hashlib.sha256()
    for name in sorted(os.listdir(SOURCES_DIR)):
        path = os.path.join(SOURCES_DIR, name)
        if os.path.isfile(path):
            h.update(name.encode())
            h.update(open(path, "rb").read())
    return h.hexdigest()


def _build_index() -> list[dict]:
    entries = []
    for name in sorted(os.listdir(SOURCES_DIR)):
        path = os.path.join(SOURCES_DIR, name)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8").read()
        entries.append({"doc": name, "text": text, "embedding": llm.get_embedding(text)})
    with open(INDEX_PATH, "w") as f:
        json.dump({"fingerprint": _fingerprint(), "entries": entries}, f)
    return entries


def load_or_build_index() -> list[dict]:
    if os.path.exists(INDEX_PATH):
        cached = json.load(open(INDEX_PATH))
        if cached.get("fingerprint") == _fingerprint():
            return cached["entries"]
    return _build_index()


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    entries = load_or_build_index()
    q_embedding = llm.get_embedding(query)
    scored = [{**e, "score": llm.cosine_similarity(q_embedding, e["embedding"])} for e in entries]
    scored.sort(key=lambda e: e["score"], reverse=True)
    return scored[:top_k]
