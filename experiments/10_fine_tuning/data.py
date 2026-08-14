"""
Synthetic domain-adaptation dataset: support-chat Q&A pairs about Nimbus
Cloud Storage (the same fictional product from experiment 2's FAQ). A base
model like distilgpt2 has never heard of Nimbus, so any improvement after
fine-tuning is attributable to the fine-tune, not prior knowledge.

Each fact has 4 question phrasings. 3 are used for training, 1 is held out
for evaluation -- so eval measures whether the model learned the FACT well
enough to answer a differently-worded question, not just memorized exact
training strings.
"""

FACTS = [
    {
        "answer": "Nimbus offers three plans: Free with 5GB storage, Plus with 200GB for $4.99/month, and Pro with 2TB for $14.99/month.",
        "questions": [
            "What plans does Nimbus offer?",
            "Can you tell me about Nimbus pricing plans?",
            "What are the storage tiers available?",
            "How much does Nimbus cost?",
        ],
    },
    {
        "answer": "Annual subscriptions can be refunded in full within 30 days of purchase. Monthly subscriptions are not refundable but can be cancelled anytime.",
        "questions": [
            "What is the refund policy?",
            "Can I get my money back if I cancel?",
            "Do you offer refunds?",
            "Is my annual subscription refundable?",
        ],
    },
    {
        "answer": "The web uploader accepts files up to 10GB each on Plus and Pro plans, and 2GB each on the Free plan.",
        "questions": [
            "What is the maximum file upload size?",
            "How big of a file can I upload?",
            "Is there a limit on file size?",
            "What's the upload limit on the Free plan?",
        ],
    },
    {
        "answer": "Deleted files move to the Trash and are kept for 30 days before permanent deletion.",
        "questions": [
            "What happens when I delete a file?",
            "How long are deleted files kept?",
            "Can I recover a file I deleted?",
            "Where do deleted files go?",
        ],
    },
    {
        "answer": "Pro plan users get 180 days of version history and can restore any previous version of a file.",
        "questions": [
            "How does version history work?",
            "Can I restore an older version of a file?",
            "How long does Nimbus keep file versions?",
            "Does Nimbus have version history?",
        ],
    },
    {
        "answer": "Support is available via chat and email, Monday to Friday, 9 AM to 6 PM Eastern Time. Pro customers get priority queueing.",
        "questions": [
            "What are the support hours?",
            "How do I contact support?",
            "When is customer support available?",
            "Do Pro users get priority support?",
        ],
    },
    {
        "answer": "Files are encrypted in transit using TLS and at rest using AES-256.",
        "questions": [
            "Is my data encrypted?",
            "How does Nimbus protect my files?",
            "What encryption does Nimbus use?",
            "Is Nimbus secure?",
        ],
    },
    {
        "answer": "Pro plans include a Locked Folder feature, and Nimbus does not have access to the encryption keys used for it.",
        "questions": [
            "What is the Locked Folder feature?",
            "Can Nimbus staff see files in my Locked Folder?",
            "Is there an extra-secure folder option?",
            "Does Pro have a private folder feature?",
        ],
    },
    {
        "answer": "All paid plans include a 14-day free trial and can be cancelled at any time from the billing page.",
        "questions": [
            "Is there a free trial?",
            "How do I cancel my subscription?",
            "Can I try Nimbus before paying?",
            "Where do I go to cancel my plan?",
        ],
    },
    {
        "answer": "The Plus plan supports up to 5 devices, and the Pro plan supports unlimited devices.",
        "questions": [
            "How many devices can I sync?",
            "Is there a device limit on Plus?",
            "Can I use Nimbus on unlimited devices?",
            "What's the device limit for each plan?",
        ],
    },
]

TRAIN_EXAMPLES = []
EVAL_EXAMPLES = []
for fact in FACTS:
    train_questions, eval_question = fact["questions"][:3], fact["questions"][3]
    for q in train_questions:
        TRAIN_EXAMPLES.append(f"Customer: {q}\nSupport: {fact['answer']}")
    EVAL_EXAMPLES.append(f"Customer: {eval_question}\nSupport: {fact['answer']}")

# A few held-out prompts (question only, no answer) for qualitative
# before/after generation comparisons.
SAMPLE_PROMPTS = [
    "Customer: What's the upload limit on the Free plan?\nSupport:",
    "Customer: Do you offer refunds?\nSupport:",
    "Customer: Is there a free trial?\nSupport:",
]
