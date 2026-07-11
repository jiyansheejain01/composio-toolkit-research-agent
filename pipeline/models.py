"""
models.py
---------
Shared, lightly-typed data structures for the pipeline. Kept dependency-free
(no pydantic requirement) so every stage can run in the grading sandbox;
swap in pydantic.BaseModel 1:1 if you want runtime validation when you run
this with a real OpenAI key (the shape is identical -- see the commented
PydanticAppResearch class at the bottom for the drop-in version used by
research_agent.py's structured-output call).
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Literal

SelfServe = Literal[
    "open",                       # no account needed, or trivially free with instant key
    "freemium_signup",            # free account required, then instant key/token
    "trial_required",             # time-boxed trial required for any access
    "admin_approval_required",    # org admin (not Composio) must issue the credential
    "paid_plan_required",         # must be on a paid tier before a key can even be created
    "partnership_required",       # formal partner program application
    "contact_sales_only",         # fully enterprise / no self-serve path at all
    "gated_unclear",               # evidence is ambiguous or thin
]

Buildability = Literal["Easy", "Medium", "Hard", "Impossible"]

VerificationStatus = Literal[
    "agent_verified",   # single-pass LLM research, evidence URL present, confidence >= 60
    "human_verified",   # cross-checked live against official docs during the verification sample
    "flagged",           # confidence < 60 or agent/verifier disagreement -> needs human review
    "unverified",        # not yet processed
]


@dataclass
class AppResearch:
    id: int
    name: str
    website: str
    category: str
    description: str
    auth: list[str]
    self_serve: SelfServe
    self_serve_detail: str
    api_surface: dict[str, Any]
    mcp: dict[str, Any]
    buildability: Buildability
    blocker: str | None
    evidence: str
    confidence: int
    verification_status: VerificationStatus
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_flat_row(self) -> dict[str, Any]:
        """Flattened row for CSV / pandas, matching the assignment's required columns."""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "auth": ", ".join(self.auth),
            "selfServe": self.self_serve,
            "selfServeDetail": self.self_serve_detail,
            "apiSurface_rest": self.api_surface.get("rest"),
            "apiSurface_graphql": self.api_surface.get("graphql"),
            "apiSurface_webhooks": self.api_surface.get("webhooks"),
            "apiSurface_sdks": ", ".join(self.api_surface.get("sdks", [])),
            "apiSurface_breadth": self.api_surface.get("breadth"),
            "apiSurface_docsPublic": self.api_surface.get("docs_public"),
            "mcp_official": self.mcp.get("official"),
            "mcp_community": self.mcp.get("community"),
            "mcp_notes": self.mcp.get("notes"),
            "buildability": self.buildability,
            "blocker": self.blocker or "",
            "evidence": self.evidence,
            "confidenceScore": self.confidence,
            "verificationStatus": self.verification_status,
            "notes": self.notes,
        }


@dataclass
class VerificationCheck:
    """One row of the ~20-app human/live verification sample."""
    app_id: int
    app_name: str
    field_checked: str            # e.g. "auth", "self_serve", "mcp"
    agent_answer: str
    doc_answer: str
    result: Literal["correct", "incorrect", "updated"]
    source_url: str
    note: str = ""


@dataclass
class VerificationReport:
    sample_size: int
    checks: list[VerificationCheck]
    initial_accuracy: float
    final_accuracy: float
    methodology: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_size": self.sample_size,
            "initial_accuracy": self.initial_accuracy,
            "final_accuracy": self.final_accuracy,
            "methodology": self.methodology,
            "checks": [asdict(c) for c in self.checks],
        }


# ---------------------------------------------------------------------------
# Drop-in pydantic version for use with the OpenAI/Anthropic structured-output
# call in research_agent.py, once real dependencies are installed:
#
# from pydantic import BaseModel
#
# class PydanticAppResearch(BaseModel):
#     name: str
#     category: str
#     description: str
#     auth: list[str]
#     self_serve: SelfServe
#     self_serve_detail: str
#     api_surface: dict[str, Any]
#     mcp: dict[str, Any]
#     buildability: Buildability
#     blocker: str | None
#     evidence: str
#     confidence: int
#     notes: str = ""
# ---------------------------------------------------------------------------
