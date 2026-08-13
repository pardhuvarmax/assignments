"""
Static synthetic data for the SDR pipeline: what we're selling, who we're
selling to, and a pool of candidate companies (fictional) to run the
pipeline against. No real companies, contacts, or emails are used anywhere
in this experiment.
"""

PRODUCT_DESCRIPTION = (
    "Nimbus Cloud Storage for Teams: encrypted cloud file sync and sharing "
    "for distributed teams, with 180-day version history, offline-synced "
    "folders, and per-folder access controls. Priced for teams of 20-1000."
)

ICP_DESCRIPTION = (
    "Mid-size companies (roughly 50-1000 employees) with distributed or "
    "multi-location teams that regularly share large or sensitive files "
    "(legal, healthcare, financial, or creative assets) and have an "
    "identifiable IT/Ops decision-maker."
)

# A synthetic "market universe" the lead-gen agent works from. Deliberately
# includes some poor-fit companies (too small, no clear digital pain point)
# so qualification has something real to filter out.
LEAD_POOL = [
    {
        "company": "Solstice Legal Partners",
        "industry": "Legal services",
        "employees": 220,
        "contact_name": "Dana Whitfield",
        "contact_title": "IT Director",
        "pain_point": "Sharing case files securely with outside counsel and expert witnesses.",
    },
    {
        "company": "BrightPath Health Clinics",
        "industry": "Healthcare",
        "employees": 340,
        "contact_name": "Marcus Ibe",
        "contact_title": "VP of IT",
        "pain_point": "Needs HIPAA-compliant document sharing between clinic locations.",
    },
    {
        "company": "Kepler Analytics",
        "industry": "Data analytics (startup)",
        "employees": 25,
        "contact_name": "Ren Okafor",
        "contact_title": "Founder & CEO",
        "pain_point": "Internal docs are scattered across personal drives.",
    },
    {
        "company": "Northwind Freight Co",
        "industry": "Logistics",
        "employees": 900,
        "contact_name": "Grace Tanaka",
        "contact_title": "IT Manager",
        "pain_point": "Large multi-GB shipping manifests need syncing across warehouses.",
    },
    {
        "company": "Ledger & Co Accounting",
        "industry": "Accounting",
        "employees": 150,
        "contact_name": "Oscar Delgado",
        "contact_title": "Head of Operations",
        "pain_point": "Client tax documents scattered across email attachments.",
    },
    {
        "company": "PixelForge Studios",
        "industry": "Game development",
        "employees": 60,
        "contact_name": "Ivy Chen",
        "contact_title": "Studio Operations Lead",
        "pain_point": "Large game asset files need version history when artists overwrite work.",
    },
    {
        "company": "Anchor Bank Retail",
        "industry": "Retail banking",
        "employees": 40,
        "contact_name": "Walt Simmons",
        "contact_title": "Branch Operations Coordinator",
        "pain_point": "Mostly paper-based branch processes; no specific file-sharing complaint.",
    },
    {
        "company": "Vertex Consulting Group",
        "industry": "Management consulting",
        "employees": 280,
        "contact_name": "Priya Raman",
        "contact_title": "VP of IT",
        "pain_point": "Consultants travel constantly and need folders that stay synced offline.",
    },
]
