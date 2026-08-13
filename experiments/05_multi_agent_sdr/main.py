import os
import sys
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data import PRODUCT_DESCRIPTION, ICP_DESCRIPTION, LEAD_POOL
from agents import lead_gen_agent, qualification_agent, outreach_agent

OUTBOX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outbox")


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def save_to_outbox(emails: list[dict]):
    os.makedirs(OUTBOX_DIR, exist_ok=True)
    for email in emails:
        path = os.path.join(OUTBOX_DIR, f"{slugify(email['company'])}.txt")
        with open(path, "w") as f:
            f.write(f"To: {email['contact_name']} <{email['contact_title']}, {email['company']}>\n")
            f.write(f"Subject: {email['subject']}\n\n")
            f.write(email["body"] + "\n")
    return OUTBOX_DIR


def main():
    print("=" * 70)
    print("  Experiment 5: Multi-Agent SDR System")
    print("  LeadGenAgent -> QualificationAgent -> OutreachAgent (mock send)")
    print("=" * 70)
    print(f"\nProduct: {PRODUCT_DESCRIPTION}")
    print(f"\nICP: {ICP_DESCRIPTION}")
    print(f"\nCandidate pool: {len(LEAD_POOL)} companies")

    print("\n--- Stage 1: LeadGenAgent ---")
    shortlist = lead_gen_agent(ICP_DESCRIPTION, LEAD_POOL)
    for lead in shortlist:
        print(f"  + {lead['company']}: {lead['fit_reason']}")
    if not shortlist:
        print("  (no leads matched the ICP -- stopping here)")
        return

    print("\n--- Stage 2: QualificationAgent ---")
    scored = qualification_agent(PRODUCT_DESCRIPTION, shortlist)
    for lead in scored:
        mark = "QUALIFIED" if lead["qualified"] else "not qualified"
        print(f"  [{lead['score']:>3}] {lead['company']} -- {mark}: {lead['qualification_reasoning']}")
    qualified = [lead for lead in scored if lead["qualified"]]
    if not qualified:
        print("  (no leads qualified -- stopping here)")
        return

    print("\n--- Stage 3: OutreachAgent (drafts only, nothing is sent) ---")
    emails = outreach_agent(PRODUCT_DESCRIPTION, qualified)
    for email in emails:
        print(f"\n  To: {email['contact_name']} ({email['company']})")
        print(f"  Subject: {email['subject']}")
        print(f"  {email['body']}")

    outbox = save_to_outbox(emails)
    print(f"\n{len(emails)} draft email(s) saved to {outbox}/ (not sent).")

    print("\n--- Summary ---")
    print(f"  Candidate pool:  {len(LEAD_POOL)}")
    print(f"  Shortlisted:     {len(shortlist)}")
    print(f"  Qualified:       {len(qualified)}")
    print(f"  Emails drafted:  {len(emails)}")


if __name__ == "__main__":
    main()
