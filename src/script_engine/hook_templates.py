"""
Proven hook formulas for short-form video scripts.

Each template contains {topic_hook} as the insertion point.
The hook_style comes from config.yaml → script.hook_style.
"""

from typing import Literal

HookStyle = Literal["question", "shocking_stat", "bold_claim"]

HOOK_TEMPLATES: dict[HookStyle, list[str]] = {
    "question": [
        "Did you know that {topic_hook}?",
        "What if I told you {topic_hook}?",
        "Why does nobody talk about {topic_hook}?",
        "Can you guess what's actually happening with {topic_hook}?",
        "Have you ever wondered why {topic_hook}?",
        "What would happen if {topic_hook}?",
    ],
    "shocking_stat": [
        "99% of people don't know this about {topic_hook}.",
        "This one fact about {topic_hook} will blow your mind.",
        "Scientists just discovered something insane about {topic_hook}.",
        "The numbers behind {topic_hook} are absolutely wild.",
        "Most people have no idea how extreme {topic_hook} actually is.",
    ],
    "bold_claim": [
        "Everything you know about {topic_hook} is wrong.",
        "This changes everything about {topic_hook}.",
        "{topic_hook} — and nobody is talking about it.",
        "The truth about {topic_hook} is stranger than fiction.",
        "{topic_hook} just got completely flipped on its head.",
    ],
}

# CTA templates — appended to the end of every script
CTA_TEMPLATES: list[str] = [
    "Follow for more mind-blowing facts like this.",
    "Follow for more facts that'll change how you see the world.",
    "Like and follow — I drop facts like this every day.",
    "Follow for more — you won't believe what's coming next.",
    "Hit follow for your daily dose of amazing facts.",
]


def get_hook(style: HookStyle, topic_hook: str, seed: int = 0) -> str:
    """
    Return a filled-in hook string for a given style and topic.

    Args:
        style: One of "question", "shocking_stat", or "bold_claim".
        topic_hook: Short topic description to insert into the template.
        seed: Index offset for template variety (use video index or hash).

    Returns:
        Formatted hook string.
    """
    templates = HOOK_TEMPLATES.get(style, HOOK_TEMPLATES["question"])
    template = templates[seed % len(templates)]
    return template.format(topic_hook=topic_hook)


def get_cta(seed: int = 0) -> str:
    """
    Return a CTA string.

    Args:
        seed: Varies which CTA is selected.

    Returns:
        CTA string.
    """
    return CTA_TEMPLATES[seed % len(CTA_TEMPLATES)]
