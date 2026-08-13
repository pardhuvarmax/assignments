"""
Experiment 7: Deep Research Agent Workflow

Plan -> Research (retrieve) -> Draft -> Reflect -> Revise. Four LLM calls
total per run (retrieval embeddings don't count against the same quota):

    1. plan()    - break the research question into sub-questions
    2. draft()   - retrieve context per sub-question, draft all sections
                   in one batched call, grounded ONLY in retrieved memos
    3. reflect() - critique the combined draft for gaps/imbalance
    4. revise()  - produce the final report incorporating the critique

The "research" in step 2 is retrieval over a small local corpus of
fictional internal memos (sources/), not live web search -- there's no
search tool in this environment, and grounding in a fixed corpus makes it
possible to check whether the agent actually reflects its sources instead
of just generating plausible-sounding text.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm
from retriever import retrieve


def plan(topic: str) -> list[str]:
    system = (
        "You are a research planning agent. Given a research question, "
        "produce 4-5 sub-questions that together would let someone answer "
        "the main question thoroughly and from multiple angles (e.g. "
        "impact on output/productivity, people/wellbeing, operational risk, "
        "financial cost, and precedent/comparison where relevant). "
        'Respond with JSON: {"sub_questions": ["...", ...]}'
    )
    result = llm.generate_json(f"Research question: {topic}", system_instruction=system)
    return result.get("sub_questions", [])


def research(sub_questions: list[str], top_k: int = 2) -> list[dict]:
    """Pure retrieval, no LLM call -- gathers grounding context per sub-question."""
    findings = []
    for q in sub_questions:
        hits = retrieve(q, top_k=top_k)
        findings.append({
            "sub_question": q,
            "sources": [{"doc": h["doc"], "text": h["text"]} for h in hits],
        })
    return findings


def draft(topic: str, findings: list[dict]) -> list[dict]:
    context_blocks = []
    for f in findings:
        sources_text = "\n\n".join(f"[{s['doc']}]\n{s['text']}" for s in f["sources"])
        context_blocks.append(f"Sub-question: {f['sub_question']}\n\nRetrieved memos:\n{sources_text}")
    combined_context = "\n\n---\n\n".join(context_blocks)

    system = (
        "You are a research drafting agent. For each sub-question below, "
        "write a grounded 100-150 word section using ONLY the retrieved "
        "memos provided for that sub-question -- cite the memo filename "
        "in parentheses for specific claims. If the memos don't fully "
        "answer the sub-question, say so explicitly rather than filling "
        "the gap with speculation. Respond with JSON: "
        '{"sections": [{"sub_question": "...", "content": "..."}]}'
    )
    prompt = f"Research question: {topic}\n\n{combined_context}"
    result = llm.generate_json(prompt, system_instruction=system)
    return result.get("sections", [])


def reflect(topic: str, sections: list[dict]) -> str:
    draft_text = "\n\n".join(f"## {s['sub_question']}\n{s['content']}" for s in sections)
    system = (
        "You are a critical editor reviewing a draft research report before "
        "it goes to leadership. Identify: (1) any important consideration "
        "that's missing or underdeveloped, (2) whether the report is "
        "balanced (covers both benefits AND risks/costs, not just one "
        "side), (3) any claim that's vague where the draft actually had "
        "more specific information available. Be concise and concrete -- a "
        "short bulleted list, not generic praise."
    )
    prompt = f"Research question: {topic}\n\nDraft report:\n{draft_text}"
    return llm.generate_text(prompt, system_instruction=system)


def revise(topic: str, sections: list[dict], critique: str) -> str:
    draft_text = "\n\n".join(f"## {s['sub_question']}\n{s['content']}" for s in sections)
    system = (
        "You are a research report writer. Revise the draft below to "
        "address the editor's critique, producing a polished final report "
        "in markdown with a short title, a one-paragraph executive summary, "
        "one section per sub-question (keep the existing grounded content, "
        "improve it), and a final 'Recommendation' section that takes a "
        "clear position while acknowledging the key risk from the critique."
    )
    prompt = f"Research question: {topic}\n\nDraft report:\n{draft_text}\n\nEditor's critique:\n{critique}"
    return llm.generate_text(prompt, system_instruction=system)


def run(topic: str, on_stage=None) -> str:
    on_stage = on_stage or (lambda **kwargs: None)

    sub_questions = plan(topic)
    on_stage(stage="plan", sub_questions=sub_questions)
    if not sub_questions:
        return "Could not produce a research plan (LLM unavailable or returned no sub-questions)."

    findings = research(sub_questions)
    on_stage(stage="research", findings=findings)

    sections = draft(topic, findings)
    on_stage(stage="draft", sections=sections)
    if not sections:
        return "Could not draft any sections (LLM unavailable or returned no content)."

    critique = reflect(topic, sections)
    on_stage(stage="reflect", critique=critique)

    final_report = revise(topic, sections, critique)
    on_stage(stage="revise", final_report=final_report)

    return final_report
