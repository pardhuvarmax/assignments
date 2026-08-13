"""
Experiment 5: Multi-Agent SDR System

Three agents hand off structured state to each other:

    LeadGenAgent -> QualificationAgent -> OutreachAgent

Each agent has its own narrow role and system prompt. Every stage makes a
single batched LLM call covering all leads at once (rather than one call
per lead) -- both cheaper and a more realistic way to keep the pipeline
usable under a tight API quota.

"Emailing" is always mocked: OutreachAgent only drafts email text, it never
sends anything. main.py writes the drafts to a local outbox/ folder.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm


def _leads_as_text(leads: list[dict]) -> str:
    lines = []
    for lead in leads:
        lines.append(
            f"- {lead['company']} | industry: {lead['industry']} | "
            f"employees: {lead['employees']} | contact: {lead['contact_name']} "
            f"({lead['contact_title']}) | stated pain point: {lead['pain_point']}"
        )
    return "\n".join(lines)


def lead_gen_agent(icp: str, pool: list[dict]) -> list[dict]:
    """Shortlists the pool down to companies that plausibly match the ICP."""
    system = (
        "You are a Lead Generation agent for a B2B SDR team. Given an Ideal "
        "Customer Profile (ICP) and a pool of candidate companies, select "
        "every company that plausibly matches the ICP. Do not invent new "
        "companies. Respond with JSON: "
        '{"shortlist": [{"company": "<name>", "fit_reason": "<one sentence>"}]}'
    )
    prompt = f"ICP:\n{icp}\n\nCandidate pool:\n{_leads_as_text(pool)}"
    result = llm.generate_json(prompt, system_instruction=system)
    shortlist = result.get("shortlist", [])

    by_name = {lead["company"]: lead for lead in pool}
    enriched = []
    for entry in shortlist:
        lead = by_name.get(entry.get("company"))
        if lead:
            enriched.append({**lead, "fit_reason": entry.get("fit_reason", "")})
    return enriched


def qualification_agent(product: str, shortlist: list[dict]) -> list[dict]:
    """Scores each shortlisted lead and decides who's worth outreach."""
    system = (
        "You are a Qualification agent for a B2B SDR team. Given the "
        "product being sold and a shortlist of leads, evaluate each one "
        "using need (does their pain point match what the product solves), "
        "authority (can this contact's title plausibly buy or champion "
        "this), and company size fit. Score 0-100 and mark qualified=true "
        "only for reasonably strong fits. Respond with JSON: "
        '{"results": [{"company": "<name>", "score": <0-100>, '
        '"qualified": <bool>, "reasoning": "<one sentence>"}]}'
    )
    prompt = f"Product:\n{product}\n\nShortlisted leads:\n{_leads_as_text(shortlist)}"
    result = llm.generate_json(prompt, system_instruction=system)
    results = result.get("results", [])

    by_name = {lead["company"]: lead for lead in shortlist}
    enriched = []
    for entry in results:
        lead = by_name.get(entry.get("company"))
        if lead:
            enriched.append({
                **lead,
                "score": entry.get("score", 0),
                "qualified": bool(entry.get("qualified", False)),
                "qualification_reasoning": entry.get("reasoning", ""),
            })
    return enriched


def outreach_agent(product: str, qualified_leads: list[dict]) -> list[dict]:
    """Drafts one personalized outreach email per qualified lead. Never sends."""
    if not qualified_leads:
        return []

    system = (
        "You are an Outreach agent for a B2B SDR team. Draft one short "
        "(under 120 words), personalized cold email per lead, referencing "
        "their specific pain point and industry. Friendly, concrete, one "
        "clear call to action to book a 15-minute call. No generic filler. "
        'Respond with JSON: {"emails": [{"company": "<name>", '
        '"subject": "<subject line>", "body": "<email body>"}]}'
    )
    prompt = f"Product:\n{product}\n\nQualified leads:\n{_leads_as_text(qualified_leads)}"
    result = llm.generate_json(prompt, system_instruction=system)
    emails = result.get("emails", [])

    by_name = {lead["company"]: lead for lead in qualified_leads}
    enriched = []
    for entry in emails:
        lead = by_name.get(entry.get("company"))
        if lead:
            enriched.append({
                **lead,
                "subject": entry.get("subject", ""),
                "body": entry.get("body", ""),
            })
    return enriched
