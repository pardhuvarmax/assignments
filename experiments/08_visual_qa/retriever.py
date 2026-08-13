"""
Text-to-image retrieval: embed the query, rank images by cosine similarity
against their caption embeddings (see indexer.py for how captions are
produced).
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm
from indexer import load_or_build_index


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    entries = load_or_build_index()
    q_embedding = llm.get_embedding(query)

    scored = []
    for name, entry in entries.items():
        score = llm.cosine_similarity(q_embedding, entry["embedding"])
        scored.append({"image": name, "caption": entry["caption"], "score": score})

    scored.sort(key=lambda e: e["score"], reverse=True)
    return scored[:top_k]
