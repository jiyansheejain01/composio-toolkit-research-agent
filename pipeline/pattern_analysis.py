"""
pattern_analysis.py
--------------------
Stage 8 of the pipeline: automatic pattern discovery over the verified
dataset. This is the "find the patterns, not just 100 rows" requirement --
every number here is computed live from data/apps.json with pandas, not
hand-typed.
"""

from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

import pandas as pd


def _self_serve_points(self_serve: str) -> int:
    return {
        "open": 30, "freemium_signup": 30, "trial_required": 20,
        "admin_approval_required": 15, "gated_unclear": 10,
        "paid_plan_required": 10, "partnership_required": 5, "contact_sales_only": 0,
    }.get(self_serve, 5)


def _buildability_points(buildability: str) -> int:
    return {"Easy": 30, "Medium": 15, "Hard": 5, "Impossible": 0}.get(buildability, 0)


def _breadth_points(surface: dict) -> int:
    b = (surface or {}).get("breadth", "") or ""
    b = b.lower()
    if "broad" in b:
        return 20
    if "medium" in b:
        return 10
    return 5


def auth_effort_tier(auth_methods: list[str]) -> str:
    """
    A rough, defensible proxy for integration effort: OAuth2 needs app
    registration + a redirect/consent flow + token refresh handling before
    a single API call succeeds; static credentials (API key / PAT / Bearer)
    are copy-paste-and-go. This is intentionally a coarse heuristic, not a
    precise engineering estimate -- it is meant to explain WHY OAuth-heavy
    categories take longer to onboard, not to replace real scoping.
    """
    joined = " ".join(auth_methods)
    if "OAuth2" in joined:
        return "Higher (OAuth2 app registration + consent flow + token refresh)"
    if "JWT" in joined or "Digest" in joined:
        return "Medium (signed-request or JWT auth, no consent flow)"
    if not auth_methods or "None" in joined:
        return "N/A (no auth / local tool)"
    return "Low (static API key / token / Bearer credential)"


def compute_priority_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Composio Build-Priority Score (0-100): a transparent, explainable
    composite used to rank *already-buildable* apps by how much friction
    remains before Composio could ship a toolkit for them. NOT a measure of
    how valuable/requested the app is commercially -- that signal (customer
    demand) lives outside this dataset and should be combined with this
    score by a human, not replace it.

        self-serve access model   -> up to 30 pts (open/freemium scores highest)
        buildability verdict      -> up to 30 pts (Easy scores highest)
        API breadth                -> up to 20 pts (broad scores highest)
        no official MCP yet        -> +20 pts (bigger marginal opportunity for Composio)
                                       already has an official MCP -> +0 (already covered)
    """
    def score_row(row) -> int:
        s = _self_serve_points(row["self_serve"])
        b = _buildability_points(row["buildability"])
        breadth = _breadth_points(row["api_surface"])
        mcp_gap_bonus = 0 if row["mcp"].get("official") else 20
        return s + b + breadth + mcp_gap_bonus

    df = df.copy()
    df["_priority_score"] = df.apply(score_row, axis=1)
    return df


def load_composio_crosscheck(path: str = "data/composio_crosscheck.json") -> dict:
    """
    Summarizes the Composio catalog cross-check (see pipeline/composio_client.py).
    Returns zeroed-out counts (not an error) if the file doesn't exist yet --
    this stage is optional and a fresh checkout may not have run it.

    `ran_live` is deliberately distinct from "the file exists": the stage
    always writes a file, even in OFFLINE mode (every row gets
    NOT_CHECKED_OFFLINE_MODE). Checking file existence alone would report
    "ran": true with every count at zero -- indistinguishable, to a reader,
    from "ran live and genuinely found nothing," which is a different and
    misleading claim. `ran_live` is only true if at least one row got a
    real answer (ALREADY_/NOT_YET_A_COMPOSIO_TOOLKIT).
    """
    p = Path(path)
    if not p.exists():
        return {"already": 0, "not_yet": 0, "not_checked": 0, "lookup_failed": 0,
                "auth_agreement_checked": 0, "auth_agreements": 0, "ran_live": False}
    rows = json.loads(p.read_text(encoding="utf-8"))
    already = [r for r in rows if r["composio_status"] == "ALREADY_A_COMPOSIO_TOOLKIT"]
    not_yet = sum(1 for r in rows if r["composio_status"] == "NOT_YET_A_COMPOSIO_TOOLKIT")
    agreement_checked = [r for r in already if r["agrees_with_our_finding"] is not None]
    return {
        "already": len(already),
        "not_yet": not_yet,
        "not_checked": sum(1 for r in rows if r["composio_status"] == "NOT_CHECKED_OFFLINE_MODE"),
        "lookup_failed": sum(1 for r in rows if r["composio_status"] == "LOOKUP_FAILED"),
        "auth_agreement_checked": len(agreement_checked),
        "auth_agreements": sum(1 for r in agreement_checked if r["agrees_with_our_finding"]),
        "ran_live": (len(already) + not_yet) > 0,
    }


def load_df(apps_path: str = "data/apps.json") -> pd.DataFrame:
    with open(apps_path, encoding="utf-8") as f:
        apps = json.load(f)
    return pd.DataFrame(apps)


def analyze(df: pd.DataFrame) -> dict:
    n = len(df)

    # --- auth method distribution (rows can have multiple auth methods) ---
    auth_counter: Counter[str] = Counter()
    for auths in df["auth"]:
        for a in auths:
            # normalize e.g. "OAuth2 (client credentials)" -> "OAuth2"
            base = a.split(" (")[0].strip()
            auth_counter[base] += 1
    auth_distribution = dict(sorted(auth_counter.items(), key=lambda kv: -kv[1]))

    # Charting the full auth_distribution directly is a real readability bug:
    # the raw counter has 30+ long-tail variants (e.g. "SCRAM/X.509 for
    # database driver" appearing once). A donut/bar with 30+ slices is
    # unreadable regardless of chart type. For the chart (not the underlying
    # data, which stays intact above for anyone inspecting the JSON), collapse
    # to the top 7 methods + a single "Other" bucket for the long tail.
    TOP_N_AUTH = 7
    sorted_auth = list(auth_distribution.items())
    auth_distribution_chart = dict(sorted_auth[:TOP_N_AUTH])
    other_count = sum(v for _, v in sorted_auth[TOP_N_AUTH:])
    if other_count:
        auth_distribution_chart[f"Other ({len(sorted_auth) - TOP_N_AUTH} variants)"] = other_count

    oauth_count = sum(v for k, v in auth_counter.items() if "OAuth" in k)
    key_count = sum(v for k, v in auth_counter.items() if "Key" in k or "Token" in k or "Bearer" in k)

    # --- self-serve distribution ---
    self_serve_counts = df["self_serve"].value_counts().to_dict()
    open_and_freemium = self_serve_counts.get("open", 0) + self_serve_counts.get("freemium_signup", 0)
    gated = n - open_and_freemium

    # --- self-serve rate by category ---
    def is_self_serve(v: str) -> bool:
        return v in ("open", "freemium_signup")

    df["_is_self_serve"] = df["self_serve"].apply(is_self_serve)
    by_category = (
        df.groupby("category")
        .agg(total=("name", "count"), self_serve=("_is_self_serve", "sum"))
        .reset_index()
    )
    by_category["self_serve_pct"] = (by_category["self_serve"] / by_category["total"] * 100).round(1)
    by_category = by_category.sort_values("self_serve_pct", ascending=False)

    most_self_serve_category = by_category.iloc[0]["category"]
    most_gated_category = by_category.iloc[-1]["category"]

    # --- API breadth by category (rough score: broad=2, medium=1, narrow=0) ---
    def breadth_score(surface: dict) -> int:
        b = (surface or {}).get("breadth", "") or ""
        b = b.lower()
        if "broad" in b:
            return 2
        if "medium" in b:
            return 1
        return 0

    df["_breadth_score"] = df["api_surface"].apply(breadth_score)
    breadth_by_category = (
        df.groupby("category")["_breadth_score"].mean().sort_values(ascending=False).round(2).to_dict()
    )

    # --- blockers ---
    blockers = df[df["blocker"].notna() & (df["blocker"] != "")]["blocker"].tolist()
    blocker_keywords = Counter()
    for b in blockers:
        low = b.lower()
        if "partner" in low:
            blocker_keywords["Partner/reseller gate"] += 1
        elif "enterprise" in low or "contract" in low:
            blocker_keywords["Enterprise-only / contact sales"] += 1
        elif "paid" in low or "no free" in low:
            blocker_keywords["No free tier for API access"] += 1
        elif "review" in low or "approval" in low:
            blocker_keywords["Manual app/developer review required"] += 1
        elif "no public api" in low or "no independently" in low or "could not" in low:
            blocker_keywords["No public API documentation found"] += 1
        else:
            blocker_keywords["Other / product-specific"] += 1

    # --- MCP coverage ---
    mcp_official = int(df["mcp"].apply(lambda m: bool(m.get("official"))).sum())
    mcp_community = int(df["mcp"].apply(lambda m: bool(m.get("community")) and not m.get("official")).sum())
    mcp_none = n - mcp_official - mcp_community

    # --- buildability distribution ---
    buildability_counts = df["buildability"].value_counts().to_dict()

    # --- opportunity buckets for Composio ---
    easy_wins = df[(df["buildability"] == "Easy") & (df["mcp"].apply(lambda m: not m.get("official")))]["name"].tolist()
    needs_outreach = df[df["self_serve"].isin(["admin_approval_required", "partnership_required"])]["name"].tolist()
    enterprise_only = df[df["self_serve"] == "contact_sales_only"]["name"].tolist()
    missing_apis = df[df["buildability"].isin(["Hard", "Impossible"])]["name"].tolist()

    # --- documentation quality proxy ---
    docs_public_pct = round(df["api_surface"].apply(lambda s: bool(s.get("docs_public"))).mean() * 100, 1)

    # --- confidence / verification health ---
    avg_confidence = round(df["confidence"].mean(), 1)
    verification_counts = df["verification_status"].value_counts().to_dict()

    # --- Composio Build-Priority Score: top actionable targets ---
    scored_df = compute_priority_scores(df)
    top_priority = (
        scored_df.sort_values(["_priority_score", "confidence"], ascending=[False, False])
        .head(10)[["name", "category", "buildability", "self_serve", "confidence", "_priority_score"]]
        .rename(columns={"_priority_score": "priority_score"})
        .to_dict(orient="records")
    )

    # --- auth effort tiering: which auth methods create the most friction ---
    df["_auth_effort"] = df["auth"].apply(auth_effort_tier)
    auth_effort_counts = df["_auth_effort"].value_counts().to_dict()
    auth_effort_by_category = (
        df.groupby("category")["_auth_effort"]
        .apply(lambda s: (s == "Higher (OAuth2 app registration + consent flow + token refresh)").mean() * 100)
        .round(1).sort_values(ascending=False).to_dict()
    )

    # --- category-level integration recommendation ---
    category_recommendation = {}
    for cat in df["category"].unique():
        cat_df = df[df["category"] == cat]
        ss_pct = round(cat_df["_is_self_serve"].mean() * 100, 1)
        mcp_pct = round(cat_df["mcp"].apply(lambda m: bool(m.get("official") or m.get("community"))).mean() * 100, 1)
        if ss_pct >= 80 and mcp_pct < 50:
            rec = "Prioritize now: highly self-serve, MCP coverage still low -- clear whitespace."
        elif ss_pct >= 80:
            rec = "Mature category: mostly self-serve, MCP coverage already forming -- differentiate on depth/reliability, not just access."
        elif ss_pct < 50:
            rec = "Requires BD motion: majority gated behind admin/partner/sales approval -- budget outreach time, not just engineering time."
        else:
            rec = "Mixed: triage app-by-app rather than treating the category uniformly."
        category_recommendation[cat] = {"self_serve_pct": ss_pct, "mcp_coverage_pct": mcp_pct, "recommendation": rec}

    return {
        "total_apps": n,
        "auth_distribution": auth_distribution,
        "auth_distribution_chart": auth_distribution_chart,
        "oauth_vs_key_pct": {
            "oauth_pct": round(oauth_count / n * 100, 1),
            "key_or_token_pct": round(key_count / n * 100, 1),
        },
        "self_serve_counts": self_serve_counts,
        "self_serve_open_pct": round(open_and_freemium / n * 100, 1),
        "gated_pct": round(gated / n * 100, 1),
        "self_serve_by_category": by_category.to_dict(orient="records"),
        "most_self_serve_category": most_self_serve_category,
        "most_gated_category": most_gated_category,
        "breadth_by_category": breadth_by_category,
        "top_blockers": dict(blocker_keywords.most_common()),
        "mcp_official_count": mcp_official,
        "mcp_community_count": mcp_community,
        "mcp_none_count": mcp_none,
        "mcp_official_pct": round(mcp_official / n * 100, 1),
        "mcp_any_pct": round((mcp_official + mcp_community) / n * 100, 1),
        "mcp_none_pct": round(mcp_none / n * 100, 1),
        "buildability_counts": buildability_counts,
        "docs_public_pct": docs_public_pct,
        "avg_confidence": avg_confidence,
        "verification_counts": verification_counts,
        "top_priority_targets": top_priority,
        "auth_effort_counts": auth_effort_counts,
        "auth_effort_by_category_oauth_pct": auth_effort_by_category,
        "category_recommendation": category_recommendation,
        "composio_crosscheck": load_composio_crosscheck(),
        "opportunities": {
            "easy_wins": easy_wins,
            "needs_outreach": needs_outreach,
            "enterprise_only": enterprise_only,
            "missing_or_hard_apis": missing_apis,
        },
    }


def save(insights: dict, out_path: str = "data/pattern_insights.json") -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(insights, f, indent=2)
    print(f"[pattern_analysis] wrote insights -> {out_path}")


if __name__ == "__main__":
    df = load_df()
    insights = analyze(df)
    save(insights)
    print(json.dumps({k: v for k, v in insights.items() if not isinstance(v, (dict, list))}, indent=2))
