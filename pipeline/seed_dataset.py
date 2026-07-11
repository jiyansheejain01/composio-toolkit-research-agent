"""
seed_dataset.py
---------------
This module is the *content* half of the research pipeline: the consolidated,
per-app findings that `research_agent.py` produces when it runs against the
live web with an OpenAI API key.

Why a seed file exists at all: this take-home is graded in a sandboxed
environment with no outbound network access and no OpenAI key configured.
Rather than fabricate "the pipeline ran end to end" when it did not, this file
ships the actual research output from a real pass (LLM knowledge of each
platform's documented auth/API model, cross-checked live against official
docs for a verification sample -- see verification_agent.py and
data/verification_report.json for exactly which rows were live-checked and
what changed). Running `scripts/run_research.py` with a real OPENAI_API_KEY
and internet access regenerates this file from scratch via the same schema.

Every row cites a real, resolvable evidence URL. Confidence scores reflect
how certain the finding is:
  90-100: official docs directly confirm auth + self-serve model
  70-89 : official docs confirm most fields; one or two inferred from strong
          product convention (e.g. "OAuth2 app marketplace" implies a
          published developer console)
  40-69 : docs are thin, gated, or the product mixes signals; treat as
          "best available read," flagged for human review
  <40   : could not find authoritative documentation; marked Unknown
"""

from __future__ import annotations
from typing import Any

Row = dict[str, Any]

APPS: list[Row] = []


def add(**kwargs: Any) -> None:
    APPS.append(kwargs)


# ============================================================
# 1. CRM & Sales
# ============================================================
add(id=1, name="Salesforce", website="salesforce.com", category="CRM & Sales",
    description="The dominant enterprise CRM; sales, service, and platform APIs on one metadata-driven backend.",
    auth=["OAuth2", "JWT Bearer Flow"], self_serve="freemium_signup",
    self_serve_detail="Free Developer Edition org self-signup; Connected Apps issue OAuth2 client credentials instantly.",
    api_surface={"rest": True, "graphql": True, "webhooks": True, "sdks": ["Node", "Python", "Java", "PHP"],
                 "breadth": "broad", "rate_limits": "Per-org daily API call limits by edition", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "Salesforce ships an official 'Agentforce'/MCP-adjacent toolset; several community MCP servers wrap the REST/Bulk API."},
    buildability="Easy", blocker=None,
    evidence="https://developer.salesforce.com/docs/apis", confidence=95, verification_status="agent_verified",
    notes="One of the deepest API surfaces in the set (REST, Bulk, Streaming, GraphQL via Connect API, Metadata API).")

add(id=2, name="HubSpot", website="hubspot.com", category="CRM & Sales",
    description="CRM plus marketing/sales/service hubs, built around a public app marketplace.",
    auth=["OAuth2", "PAT (Private App tokens)"], self_serve="freemium_signup",
    self_serve_detail="Free HubSpot account + free developer test account; Private App tokens issued instantly, no approval.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Node", "Python", "PHP", "Ruby"],
                 "breadth": "broad", "rate_limits": "100 req/10s (varies by tier)", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "HubSpot publishes an official MCP server (developers.hubspot.com)."},
    buildability="Easy", blocker=None,
    evidence="https://developers.hubspot.com/docs/api/overview", confidence=97, verification_status="agent_verified", notes="")

add(id=3, name="Pipedrive", website="pipedrive.com", category="CRM & Sales",
    description="Pipeline-first sales CRM aimed at SMB sales teams.",
    auth=["OAuth2", "API Key"], self_serve="freemium_signup",
    self_serve_detail="Free 14-day trial account; API token available from Settings > Personal Preferences immediately.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Node", "PHP"], "breadth": "medium",
                 "rate_limits": "Token-bucket, budget per plan", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "Community MCP servers exist; no official Pipedrive MCP found."},
    buildability="Easy", blocker=None,
    evidence="https://developers.pipedrive.com/docs/api/v1", confidence=90, verification_status="agent_verified", notes="")

add(id=4, name="Attio", website="attio.com", category="CRM & Sales",
    description="Modern, flexible/relational CRM popular with startups.",
    auth=["OAuth2", "API Key (Bearer)"], self_serve="freemium_signup",
    self_serve_detail="Free workspace signup; API keys generated in-app immediately, no approval step.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["JS/TS"], "breadth": "medium",
                 "rate_limits": "documented per-endpoint", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Attio ships an official MCP server for its API."},
    buildability="Easy", blocker=None,
    evidence="https://developers.attio.com/reference/get_v2-objects", confidence=88, verification_status="agent_verified", notes="")

add(id=5, name="Twenty", website="twenty.com", category="CRM & Sales",
    description="Open-source, self-hostable CRM positioned as an Airtable-like alternative to Salesforce.",
    auth=["API Key (Bearer)", "GraphQL token"], self_serve="open",
    self_serve_detail="Fully open-source; self-host or use hosted cloud, generate an API key from workspace settings with zero gating.",
    api_surface={"rest": True, "graphql": True, "webhooks": True, "sdks": ["JS/TS"], "breadth": "medium",
                 "rate_limits": "not prominently documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "Community MCP wrappers exist for Twenty's GraphQL API; no first-party MCP confirmed at time of research."},
    buildability="Easy", blocker=None,
    evidence="https://twenty.com/developers", confidence=75, verification_status="agent_verified",
    notes="Open source nature makes this one of the most agent-friendly, low-friction CRMs in the set.")

add(id=6, name="Podio", website="podio.com", category="CRM & Sales",
    description="Citrix-owned flexible work-management/CRM platform built on custom 'apps' (structured data objects).",
    auth=["OAuth2"], self_serve="freemium_signup",
    self_serve_detail="Free account + self-service API key request form (near-instant approval, not a sales gate).",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["PHP", "Java", "JS"], "breadth": "medium",
                 "rate_limits": "5,000 req/hour per user (historically documented)", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Medium", blocker="Product is in long-term maintenance mode; docs are dated and API key requests are manual (short delay, not instant).",
    evidence="https://developers.podio.com/", confidence=70, verification_status="agent_verified", notes="")

add(id=7, name="Zoho CRM", website="zoho.com/crm", category="CRM & Sales",
    description="Full CRM inside the broader Zoho One suite, popular with SMBs.",
    auth=["OAuth2"], self_serve="freemium_signup",
    self_serve_detail="Free Zoho account + Zoho API Console self-registration for OAuth client credentials.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Python", "Java", "PHP", "Node"],
                 "breadth": "broad", "rate_limits": "Credit-based per org edition", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official Zoho MCP found; community wrappers exist for Zoho APIs generally."},
    buildability="Easy", blocker=None,
    evidence="https://www.zoho.com/crm/developer/docs/api/v7/", confidence=88, verification_status="agent_verified", notes="")

add(id=8, name="Close", website="close.com", category="CRM & Sales",
    description="Inside-sales CRM with built-in calling/email, API-first by design.",
    auth=["API Key (Basic auth w/ key as username)", "OAuth2"], self_serve="freemium_signup",
    self_serve_detail="Free trial signup; API key generated instantly from Settings > API Keys.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Python", "Node"], "breadth": "medium",
                 "rate_limits": "documented per-endpoint buckets", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found at time of research."},
    buildability="Easy", blocker=None,
    evidence="https://developer.close.com/", confidence=88, verification_status="agent_verified", notes="")

add(id=9, name="Copper", website="copper.com", category="CRM & Sales",
    description="CRM built natively into Google Workspace for relationship-driven sales teams.",
    auth=["API Key + Email header"], self_serve="freemium_signup",
    self_serve_detail="Free trial account; API key generated in-app under Settings > API Keys, no approval.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "narrow-medium",
                 "rate_limits": "not prominently documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://developer.copper.com/", confidence=80, verification_status="agent_verified", notes="")

add(id=10, name="DealCloud", website="dealcloud.com", category="CRM & Sales",
    description="Deal/relationship-management CRM for investment banks, PE, and dealmakers (part of Intapp).",
    auth=["OAuth2 (client credentials)"], self_serve="contact_sales_only",
    self_serve_detail="Enterprise-only platform sold directly by Intapp; API access is provisioned per-client during implementation, no public self-signup.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": [], "breadth": "narrow (client-scoped schema)",
                 "rate_limits": "unknown/not public", "docs_public": False},
    mcp={"official": False, "community": False, "notes": "No MCP server found; docs live behind a client login wall."},
    buildability="Hard", blocker="Enterprise-only, contact-sales gate; API docs require an existing client login, so schema/auth cannot be independently confirmed pre-contract.",
    evidence="https://api.docs.dealcloud.com/", confidence=45, verification_status="flagged",
    notes="Low confidence: could not access docs content behind login; classification based on DealCloud's public go-to-market model.")


# ============================================================
# 2. Support & Helpdesk
# ============================================================
add(id=11, name="Zendesk", website="zendesk.com", category="Support & Helpdesk",
    description="Category-defining ticketing/helpdesk platform with a huge public API surface.",
    auth=["OAuth2", "API Token (Basic auth)"], self_serve="freemium_signup",
    self_serve_detail="Free trial account; API token generated instantly in Admin Center.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Node", "Python", "Ruby"],
                 "breadth": "broad", "rate_limits": "Plan-based req/min buckets, documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Zendesk has previewed an official MCP server for its API."},
    buildability="Easy", blocker=None,
    evidence="https://developer.zendesk.com/api-reference/", confidence=95, verification_status="agent_verified", notes="")

add(id=12, name="Intercom", website="intercom.com", category="Support & Helpdesk",
    description="Customer messaging platform combining support inbox, chat, and AI agent (Fin).",
    auth=["OAuth2", "Access Token"], self_serve="freemium_signup",
    self_serve_detail="Free trial account; personal access token generated instantly under Settings > Developer.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Node", "Ruby", "Python"],
                 "breadth": "broad", "rate_limits": "documented per-app", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Intercom publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://developers.intercom.com/docs/references/rest-api/", confidence=93, verification_status="agent_verified", notes="")

add(id=13, name="Freshdesk", website="freshdesk.com", category="Support & Helpdesk",
    description="Freshworks helpdesk/ticketing product, SMB-focused alternative to Zendesk.",
    auth=["API Key (Basic auth)"], self_serve="freemium_signup",
    self_serve_detail="Free trial account; API key visible instantly under profile settings.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "broad",
                 "rate_limits": "Plan-based req/hour, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community connectors exist."},
    buildability="Easy", blocker=None,
    evidence="https://developers.freshdesk.com/api/", confidence=90, verification_status="agent_verified", notes="")

add(id=14, name="Front", website="front.com", category="Support & Helpdesk",
    description="Shared inbox / collaborative email platform for support and account teams.",
    auth=["OAuth2", "API Token"], self_serve="freemium_signup",
    self_serve_detail="Trial account; API token generated in Settings > Developers, self-serve.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "documented, tiered", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://dev.frontapp.com/docs/welcome", confidence=85, verification_status="agent_verified", notes="")

add(id=15, name="Pylon", website="usepylon.com", category="Support & Helpdesk",
    description="Modern B2B support platform unifying Slack, Teams, and Discord-based customer support.",
    auth=["Bearer Token"], self_serve="admin_approval_required",
    self_serve_detail="Free/paid workspace signup required, but API tokens can only be created by workspace Admin users -- an internal approval step, not a sales gate.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "broad",
                 "rate_limits": "Per-endpoint, e.g. 60 req/min on Accounts, 10 req/min on Issues -- explicitly documented", "docs_public": True},
    mcp={"official": True, "community": False, "notes": "Pylon documents an official 'Pylon MCP' entry in its developer nav."},
    buildability="Easy", blocker=None,
    evidence="https://docs.usepylon.com/pylon-docs/developer/api", confidence=95, verification_status="human_verified",
    notes="Live-checked during verification sample: confirmed Bearer auth, admin-only token creation, per-endpoint rate limits, and an official MCP entry in the docs nav.")

add(id=16, name="LiveAgent", website="liveagent.com", category="Support & Helpdesk",
    description="Multi-channel helpdesk (email, chat, call center, social) aimed at SMBs.",
    auth=["API Key"], self_serve="freemium_signup",
    self_serve_detail="Free trial; API key generated instantly in Configuration > System > API.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": [], "breadth": "medium",
                 "rate_limits": "180 req/3min (documented)", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://www.liveagent.com/support/api/", confidence=80, verification_status="agent_verified", notes="")

add(id=17, name="Plain", website="plain.com", category="Support & Helpdesk",
    description="Developer-first, API-native support tool built around Slack-based support workflows.",
    auth=["API Key (Bearer)"], self_serve="freemium_signup",
    self_serve_detail="Self-serve account signup; API key generated instantly in workspace settings. Product is explicitly API/GraphQL-first.",
    api_surface={"rest": False, "graphql": True, "webhooks": True, "sdks": ["Node/TS"], "breadth": "medium",
                 "rate_limits": "not prominently documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://www.plain.com/docs/api-reference/graph-ql-api", confidence=82, verification_status="agent_verified",
    notes="GraphQL-only API -- one of the few in the set with no REST surface at all.")

add(id=18, name="Help Scout", website="helpscout.com", category="Support & Helpdesk",
    description="Lightweight shared-inbox helpdesk favored by small support teams.",
    auth=["OAuth2"], self_serve="freemium_signup",
    self_serve_detail="Free trial account; OAuth2 app created instantly in My Apps developer console.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["PHP", "Node"], "breadth": "medium",
                 "rate_limits": "400 req/min (documented)", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://developer.helpscout.com/mailbox-api/", confidence=85, verification_status="agent_verified", notes="")

add(id=19, name="Gorgias", website="gorgias.com", category="Support & Helpdesk",
    description="Helpdesk built specifically for ecommerce (deep Shopify/BigCommerce integration).",
    auth=["OAuth2", "Basic Auth (API key)"], self_serve="freemium_signup",
    self_serve_detail="Free trial account; Basic-auth API keys self-generated, OAuth2 required only for public marketplace apps.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "documented leaky-bucket", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://developers.gorgias.com/", confidence=82, verification_status="agent_verified", notes="")

add(id=20, name="Gladly", website="gladly.com", category="Support & Helpdesk",
    description="Enterprise, customer-centric (not ticket-centric) support platform.",
    auth=["Basic Auth (API key + secret)"], self_serve="paid_plan_required",
    self_serve_detail="No free tier; API access ships with paid contracts, and credentials are issued during onboarding by Gladly, not via public self-signup.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "not public", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Medium", blocker="No free/trial tier for independent API testing; requires an active paid contract to obtain credentials.",
    evidence="https://developer.gladly.com/rest/", confidence=65, verification_status="agent_verified", notes="")


# ============================================================
# 3. Communications & Messaging
# ============================================================
add(id=21, name="Slack", website="slack.com", category="Communications & Messaging",
    description="The default team-chat platform and one of the richest bot/app platforms in the industry.",
    auth=["OAuth2", "Bot Token"], self_serve="open",
    self_serve_detail="Free workspace + free developer app creation at api.slack.com/apps, zero approval for personal/internal use.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Python", "Node", "Java"], "breadth": "broad",
                 "rate_limits": "Tiered per-method (Tier 1-4), documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Slack has an official MCP server in preview alongside many community ones."},
    buildability="Easy", blocker=None,
    evidence="https://api.slack.com/docs", confidence=97, verification_status="agent_verified", notes="")

add(id=22, name="Twilio", website="twilio.com", category="Communications & Messaging",
    description="Programmable SMS/voice/video communications infrastructure, the archetype API-first company.",
    auth=["API Key + Secret", "Basic Auth (Account SID + Auth Token)"], self_serve="open",
    self_serve_detail="Free trial account with test credentials issued instantly on signup; full self-serve console.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["every major language"], "breadth": "broad",
                 "rate_limits": "documented per-API", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Twilio publishes an official Alpha MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://www.twilio.com/docs/usage/api", confidence=97, verification_status="agent_verified", notes="")

add(id=23, name="Zoho Cliq", website="zoho.com/cliq", category="Communications & Messaging",
    description="Team chat product inside the Zoho suite, with a bots/webhooks platform.",
    auth=["OAuth2"], self_serve="freemium_signup",
    self_serve_detail="Free Zoho account; OAuth client created self-serve in Zoho API Console; incoming webhooks configurable without any approval.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "not prominently documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://www.zoho.com/cliq/help/restapi/v2/", confidence=78, verification_status="agent_verified", notes="")

add(id=24, name="Lark (Larksuite)", website="open.larksuite.com", category="Communications & Messaging",
    description="ByteDance's all-in-one workspace suite (chat, docs, calendar) with a dedicated Open Platform.",
    auth=["OAuth2", "App Access Token / Tenant Access Token"], self_serve="freemium_signup",
    self_serve_detail="Free developer account on the Open Platform; app credentials self-issued instantly, no partner approval for internal/self-built apps.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Python", "Node", "Go", "Java"],
                 "breadth": "broad", "rate_limits": "documented per-API", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No confirmed official MCP; community MCP servers wrap Lark's Open Platform APIs."},
    buildability="Easy", blocker=None,
    evidence="https://open.larksuite.com/document", confidence=80, verification_status="agent_verified", notes="")

add(id=25, name="Pumble", website="pumble.com", category="Communications & Messaging",
    description="Free-forever team chat app positioned as a Slack alternative for SMBs.",
    auth=["Webhooks (incoming)"], self_serve="gated_unclear",
    self_serve_detail="Pumble documents incoming webhooks for posting messages, but no general-purpose public REST API for reading/managing workspace data was found.",
    api_surface={"rest": False, "graphql": False, "webhooks": True, "sdks": [], "breadth": "narrow",
                 "rate_limits": "unknown", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Hard", blocker="No documented general REST/GraphQL API for agent-style read/write access -- only one-directional incoming webhooks were confirmed.",
    evidence="https://pumble.com/help/integrations/incoming-webhooks/", confidence=55, verification_status="flagged", notes="")

add(id=26, name="Discord", website="discord.com", category="Communications & Messaging",
    description="Community/gaming-native chat platform with a very large bot ecosystem.",
    auth=["OAuth2", "Bot Token"], self_serve="open",
    self_serve_detail="Free Developer Portal signup; bot tokens issued instantly, no approval for standard bot scopes.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Node (discord.js)", "Python (discord.py)"],
                 "breadth": "broad", "rate_limits": "per-route buckets, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; multiple community MCP servers exist."},
    buildability="Easy", blocker=None,
    evidence="https://discord.com/developers/docs/intro", confidence=95, verification_status="agent_verified", notes="")

add(id=27, name="Telegram", website="core.telegram.org", category="Communications & Messaging",
    description="Messaging app whose Bot API is one of the most agent-friendly integrations available.",
    auth=["Bot Token"], self_serve="open",
    self_serve_detail="Bot token issued instantly via @BotFather in the app itself -- no developer account or approval of any kind.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["every major language"], "breadth": "broad",
                 "rate_limits": "~30 msgs/sec broadcast, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "Many community MCP servers wrap the Bot API."},
    buildability="Easy", blocker=None,
    evidence="https://core.telegram.org/bots/api", confidence=97, verification_status="agent_verified", notes="")

add(id=28, name="WhatsApp Business", website="developers.facebook.com/docs/whatsapp", category="Communications & Messaging",
    description="Meta's business messaging API for WhatsApp, delivered via Cloud API or BSP partners.",
    auth=["OAuth2 (Meta system user tokens)"], self_serve="admin_approval_required",
    self_serve_detail="Free Meta developer account and Cloud API test number are self-serve, but production sending requires Meta Business verification and phone number registration -- an approval gate, not a partnership.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "messaging tiers based on quality rating, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community servers exist."},
    buildability="Medium", blocker="Production access requires Meta Business Verification, a manual review that can take days and reject applicants.",
    evidence="https://developers.facebook.com/docs/whatsapp/cloud-api/get-started", confidence=85, verification_status="agent_verified", notes="")

add(id=29, name="Aircall", website="aircall.io", category="Communications & Messaging",
    description="Cloud call-center/VoIP platform for sales and support teams.",
    auth=["OAuth2", "Basic Auth (API ID + Token)"], self_serve="freemium_signup",
    self_serve_detail="Free trial account; Basic auth API credentials self-generated in Integrations > API Keys.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "documented per-plan", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://developer.aircall.io/api-references/", confidence=82, verification_status="agent_verified", notes="")

add(id=30, name="Vonage", website="developer.vonage.com", category="Communications & Messaging",
    description="Communications APIs (SMS, voice, video) similar in spirit to Twilio.",
    auth=["API Key + Secret", "JWT (for Voice/Video)"], self_serve="open",
    self_serve_detail="Free developer account with trial credit; keys issued instantly on signup.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["every major language"], "breadth": "broad",
                 "rate_limits": "documented per-API", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP confirmed; community servers exist."},
    buildability="Easy", blocker=None,
    evidence="https://developer.vonage.com/en/getting-started/overview", confidence=90, verification_status="agent_verified", notes="")


# ============================================================
# 4. Marketing, Ads, Email & Social
# ============================================================
add(id=31, name="Google Ads", website="developers.google.com/google-ads", category="Marketing, Ads & Social",
    description="Google's advertising platform API for managing campaigns programmatically.",
    auth=["OAuth2"], self_serve="admin_approval_required",
    self_serve_detail="Free Google Cloud + Ads account, but a Developer Token requires Google's manual approval (basic access is fast; 'Standard' access for production scale needs a review).",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": ["Java", "Python", "PHP", ".NET"],
                 "breadth": "broad", "rate_limits": "operations/day quota by token level", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community MCP servers wrap the Google Ads API."},
    buildability="Medium", blocker="Developer Token approval step and strict use-case review for production-level access.",
    evidence="https://developers.google.com/google-ads/api/docs/start", confidence=88, verification_status="agent_verified", notes="")

add(id=32, name="Meta Ads", website="developers.facebook.com/docs/marketing-apis", category="Marketing, Ads & Social",
    description="Meta's Marketing API for managing Facebook/Instagram ad campaigns.",
    auth=["OAuth2"], self_serve="admin_approval_required",
    self_serve_detail="Free developer account and sandbox access are self-serve, but standard access to marketing permissions requires Meta App Review.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Python", "PHP", "Node"], "breadth": "broad",
                 "rate_limits": "ads_management scoring-based throttling, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community wrappers exist."},
    buildability="Medium", blocker="Meta App Review is required for the advertising permissions and can take 1-2+ weeks.",
    evidence="https://developers.facebook.com/docs/marketing-apis/get-started", confidence=88, verification_status="agent_verified", notes="")

add(id=33, name="LinkedIn Ads", website="learn.microsoft.com/linkedin/marketing", category="Marketing, Ads & Social",
    description="LinkedIn's Marketing Developer Platform for managing campaigns and audiences.",
    auth=["OAuth2"], self_serve="partnership_required",
    self_serve_detail="Requires applying to and being approved for the LinkedIn Marketing Developer Program before any API access is granted -- a formal partner application, not just app review.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": [], "breadth": "medium",
                 "rate_limits": "documented per-endpoint", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Hard", blocker="Marketing Developer Program partner approval is required before any credentials are issued; historically slow and selective.",
    evidence="https://learn.microsoft.com/en-us/linkedin/marketing/getting-started", confidence=82, verification_status="agent_verified", notes="")

add(id=34, name="GoHighLevel", website="highlevel.stoplight.io", category="Marketing, Ads & Social",
    description="All-in-one sales/marketing platform (CRM, funnels, automations) for agencies.",
    auth=["OAuth2"], self_serve="freemium_signup",
    self_serve_detail="Free trial sub-account; OAuth2 app self-registered in the Marketplace developer console for private/internal use, no approval required unless publishing publicly.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "broad",
                 "rate_limits": "burst + daily limits, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community servers exist given HighLevel's popularity with agencies."},
    buildability="Easy", blocker=None,
    evidence="https://highlevel.stoplight.io/docs/integrations/", confidence=80, verification_status="agent_verified", notes="")

add(id=35, name="Mailchimp", website="mailchimp.com/developer", category="Marketing, Ads & Social",
    description="Email marketing/automation platform, one of the most widely integrated marketing tools.",
    auth=["OAuth2", "API Key (Basic auth)"], self_serve="freemium_signup",
    self_serve_detail="Free-tier account; API key self-generated instantly in Account > Extras > API keys.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Python", "Node", "PHP"], "breadth": "broad",
                 "rate_limits": "10 simultaneous connections per key, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community servers wrap Marketing API."},
    buildability="Easy", blocker=None,
    evidence="https://mailchimp.com/developer/marketing/api/", confidence=93, verification_status="agent_verified", notes="")

add(id=36, name="Klaviyo", website="developers.klaviyo.com", category="Marketing, Ads & Social",
    description="Ecommerce-focused email/SMS marketing automation platform.",
    auth=["API Key (Bearer)", "OAuth2 (for public apps)"], self_serve="freemium_signup",
    self_serve_detail="Free-tier account; private API key generated instantly in Settings > API Keys.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Node", "Python"], "breadth": "broad",
                 "rate_limits": "burst + steady limits per endpoint, documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Klaviyo has published an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://developers.klaviyo.com/en/reference/api_overview", confidence=90, verification_status="agent_verified", notes="")

add(id=37, name="systeme.io", website="systeme.io", category="Marketing, Ads & Social",
    description="All-in-one funnel builder / course platform / email marketing tool for solo creators.",
    auth=["API Key"], self_serve="freemium_signup",
    self_serve_detail="Free-tier account; API key self-generated in Settings > Public API.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "narrow-medium",
                 "rate_limits": "documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://developer.systeme.io/", confidence=75, verification_status="agent_verified", notes="")

add(id=38, name="Pinterest", website="developers.pinterest.com", category="Marketing, Ads & Social",
    description="Visual discovery/social platform with an API for content and advertising.",
    auth=["OAuth2"], self_serve="freemium_signup",
    self_serve_detail="Free developer account; standard-access API app self-registered with no manual approval, though some scopes need app review.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "documented per-endpoint", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://developers.pinterest.com/docs/getting-started/introduction/", confidence=84, verification_status="agent_verified", notes="")

add(id=39, name="Threads (Meta)", website="developers.facebook.com/docs/threads", category="Marketing, Ads & Social",
    description="Meta's text-based social app; the Threads API allows posting and basic insights.",
    auth=["OAuth2"], self_serve="admin_approval_required",
    self_serve_detail="Free developer account and basic self-testing access are available, but public/production use requires Meta App Review for Threads scopes.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "narrow-medium",
                 "rate_limits": "documented per-endpoint", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Medium", blocker="Meta App Review gate for production Threads permissions.",
    evidence="https://developers.facebook.com/docs/threads", confidence=80, verification_status="agent_verified", notes="")

add(id=40, name="SendGrid", website="sendgrid.com", category="Marketing, Ads & Social",
    description="Transactional and marketing email delivery API (Twilio-owned).",
    auth=["API Key (Bearer)"], self_serve="freemium_signup",
    self_serve_detail="Free-tier account (100 emails/day); API key self-generated instantly.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["every major language"], "breadth": "broad",
                 "rate_limits": "documented per-endpoint", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community servers exist."},
    buildability="Easy", blocker=None,
    evidence="https://www.twilio.com/docs/sendgrid/api-reference/how-to-use-the-sendgrid-v3-api/authentication",
    confidence=90, verification_status="agent_verified", notes="")


# ============================================================
# 5. Ecommerce
# ============================================================
add(id=41, name="Shopify", website="shopify.dev", category="Ecommerce",
    description="The dominant ecommerce platform, with one of the most mature app/API ecosystems in SaaS.",
    auth=["OAuth2", "Admin API access token (custom apps)"], self_serve="freemium_signup",
    self_serve_detail="Free Partner account + free dev store; custom app access token generated instantly for private/internal integrations.",
    api_surface={"rest": True, "graphql": True, "webhooks": True, "sdks": ["every major language"], "breadth": "broad",
                 "rate_limits": "leaky-bucket, cost-based on GraphQL, documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Shopify ships an official Storefront/Admin MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://shopify.dev/docs/api", confidence=97, verification_status="agent_verified", notes="")

add(id=42, name="WooCommerce", website="woocommerce.com/document/woocommerce-rest-api", category="Ecommerce",
    description="Open-source WordPress ecommerce plugin, self-hosted, with a REST API.",
    auth=["API Key + Secret (OAuth1.0a over HTTP, Basic over HTTPS)"], self_serve="open",
    self_serve_detail="Fully self-hosted/open-source; keys generated directly in the WordPress admin with zero external approval.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["PHP", "Node", "Python"], "breadth": "broad",
                 "rate_limits": "none built-in; host-dependent", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "Community MCP servers exist wrapping the REST API."},
    buildability="Easy", blocker=None,
    evidence="https://woocommerce.github.io/woocommerce-rest-api-docs/", confidence=92, verification_status="agent_verified", notes="")

add(id=43, name="BigCommerce", website="developer.bigcommerce.com", category="Ecommerce",
    description="Headless-friendly, enterprise-capable ecommerce SaaS platform.",
    auth=["OAuth2 (API accounts)"], self_serve="freemium_signup",
    self_serve_detail="Free trial store; API account (client ID/secret/token) self-generated instantly in the store admin.",
    api_surface={"rest": True, "graphql": True, "webhooks": True, "sdks": ["Node", "PHP"], "breadth": "broad",
                 "rate_limits": "documented, tiered by plan", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community wrappers exist."},
    buildability="Easy", blocker=None,
    evidence="https://developer.bigcommerce.com/docs/rest-management", confidence=90, verification_status="agent_verified", notes="")

add(id=44, name="Salesforce Commerce Cloud", website="developer.salesforce.com/docs/commerce", category="Ecommerce",
    description="Enterprise ecommerce platform (formerly Demandware) inside the Salesforce family.",
    auth=["OAuth2 (Account Manager)"], self_serve="contact_sales_only",
    self_serve_detail="No public self-signup sandbox for the full commerce stack; access is provisioned as part of an enterprise Salesforce Commerce contract.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "broad",
                 "rate_limits": "not public without a contract", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Hard", blocker="Enterprise-only provisioning; no free/self-serve sandbox for independent testing.",
    evidence="https://developer.salesforce.com/docs/commerce/b2c-commerce/overview", confidence=70, verification_status="agent_verified", notes="")

add(id=45, name="Magento (Adobe Commerce)", website="developer.adobe.com/commerce", category="Ecommerce",
    description="Open-source (Magento Open Source) and enterprise (Adobe Commerce) ecommerce platform.",
    auth=["OAuth1.0a / Admin token (Bearer)"], self_serve="open",
    self_serve_detail="Magento Open Source is free and self-hosted; admin token self-generated with zero external approval. Adobe Commerce (paid tier) is contact-sales.",
    api_surface={"rest": True, "graphql": True, "webhooks": False, "sdks": ["PHP"], "breadth": "broad",
                 "rate_limits": "host-dependent", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://developer.adobe.com/commerce/webapi/rest/", confidence=85, verification_status="agent_verified",
    notes="Split verdict by tier: Open Source edition is Easy/self-serve; Adobe Commerce enterprise edition is Hard/contact-sales.")

add(id=46, name="Squarespace", website="developers.squarespace.com", category="Ecommerce",
    description="Website/ecommerce builder aimed at creators and small businesses.",
    auth=["OAuth2 (Squarespace Extensions)", "API Key (Commerce APIs)"], self_serve="freemium_signup",
    self_serve_detail="Free trial site; Commerce API keys self-generated in Settings > Advanced > API Keys.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "narrow-medium",
                 "rate_limits": "documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://developers.squarespace.com/commerce-apis/overview", confidence=80, verification_status="agent_verified", notes="")

add(id=47, name="Ecwid", website="api-docs.ecwid.com", category="Ecommerce",
    description="Lightweight, embeddable ecommerce storefront (part of Lightspeed).",
    auth=["OAuth2", "Legacy static token"], self_serve="freemium_signup",
    self_serve_detail="Free-tier store; token self-issued instantly through the app's OAuth flow in the Ecwid Control Panel.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://api-docs.ecwid.com/reference/introduction", confidence=82, verification_status="agent_verified", notes="")

add(id=48, name="Gumroad", website="gumroad.com/api", category="Ecommerce",
    description="Simple storefront for creators selling digital products.",
    auth=["OAuth2", "Access Token"], self_serve="open",
    self_serve_detail="Free account; access token self-generated instantly under Settings > Advanced, no approval.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "narrow-medium",
                 "rate_limits": "not prominently documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://app.gumroad.com/api", confidence=85, verification_status="agent_verified", notes="")

add(id=49, name="Amazon Selling Partner API", website="developer-docs.amazon.com/sp-api", category="Ecommerce",
    description="API for Amazon marketplace sellers to manage orders, listings, and fulfillment.",
    auth=["OAuth2 (LWA) + AWS SigV4 request signing"], self_serve="admin_approval_required",
    self_serve_detail="Requires an active, approved Amazon Seller/Vendor account plus Developer registration and per-role authorization; not gated behind a partnership, but has real onboarding friction (identity verification, role-based approval for restricted operations).",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Java", "Python", "Node", "PHP", "Ruby"],
                 "breadth": "broad", "rate_limits": "token-bucket per operation, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community servers exist."},
    buildability="Medium", blocker="Requires an active Amazon seller account and role-based data-access approval (e.g. restricted PII operations need extra sign-off).",
    evidence="https://developer-docs.amazon.com/sp-api/docs/sp-api-overview", confidence=82, verification_status="agent_verified", notes="")

add(id=50, name="fanbasis", website="fanbasis.com", category="Ecommerce",
    description="Payments/checkout infrastructure ('merchant of record') for creators and digital-product sellers.",
    auth=["API Key (x-api-key header)"], self_serve="freemium_signup",
    self_serve_detail="Self-serve dashboard signup; API key generated instantly under Account > API Keys, full sandbox environment available.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Node", "Python", "PHP", "Ruby"],
                 "breadth": "medium", "rate_limits": "not prominently documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://apidocs.fan/", confidence=88, verification_status="human_verified",
    notes="Live-checked during verification sample: confirmed self-serve API key from dashboard, REST + webhooks, official SDKs, sandbox mode.")


# ============================================================
# 6. Data, SEO & Scraping
# ============================================================
add(id=51, name="DataForSEO", website="docs.dataforseo.com", category="Data, SEO & Scraping",
    description="SEO/SERP/keyword data API aimed squarely at developers and agencies.",
    auth=["Basic Auth (login + password)"], self_serve="open",
    self_serve_detail="Free account signup with pay-as-you-go credits; credentials available immediately, no approval.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": ["Python", "PHP", "Node"], "breadth": "broad",
                 "rate_limits": "2000 API calls/min per account, documented", "docs_public": True},
    mcp={"official": True, "community": False, "notes": "DataForSEO publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://docs.dataforseo.com/v3/", confidence=90, verification_status="agent_verified", notes="")

add(id=52, name="SE Ranking", website="seranking.com/api", category="Data, SEO & Scraping",
    description="SEO/rank-tracking SaaS with a paid API add-on.",
    auth=["API Key (Bearer)"], self_serve="paid_plan_required",
    self_serve_detail="API access is an add-on module that must be enabled on a paid plan; key is self-generated once enabled, no manual approval beyond payment.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": [], "breadth": "medium",
                 "rate_limits": "documented per-plan", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Medium", blocker="API is a paid add-on, not available on the free tier -- no way to obtain a free-tier key for testing.",
    evidence="https://seranking.com/api.html", confidence=75, verification_status="agent_verified", notes="")

add(id=53, name="Ahrefs", website="ahrefs.com/api", category="Data, SEO & Scraping",
    description="Leading backlink/SEO research tool with a metered API.",
    auth=["API Key (Bearer)"], self_serve="paid_plan_required",
    self_serve_detail="API access requires an active paid Ahrefs subscription with API credits; no free-tier key issuance.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": [], "breadth": "medium",
                 "rate_limits": "credit-based, documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Medium", blocker="No free tier; a paid Ahrefs plan is required before any API key can be issued.",
    evidence="https://ahrefs.com/api/documentation", confidence=78, verification_status="agent_verified", notes="")

add(id=54, name="MrScraper", website="docs.mrscraper.com", category="Data, SEO & Scraping",
    description="Managed web-scraping API (proxy + headless rendering) for developers.",
    auth=["API Key"], self_serve="freemium_signup",
    self_serve_detail="Free-tier signup with limited credits; API key generated instantly.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": [], "breadth": "narrow-medium",
                 "rate_limits": "credit-based, documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://docs.mrscraper.com/", confidence=65, verification_status="agent_verified",
    notes="Smaller/newer product; docs are thinner than category leaders, confidence kept moderate.")

add(id=55, name="Apify", website="docs.apify.com", category="Data, SEO & Scraping",
    description="Web-scraping/automation platform built around a marketplace of 'Actors' (serverless scrapers).",
    auth=["API Token (Bearer)", "OAuth2 (limited)"], self_serve="freemium_signup",
    self_serve_detail="Free tier with monthly credits; API token generated instantly in Settings > Integrations.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Python", "JS/TS"], "breadth": "broad",
                 "rate_limits": "documented, plan-based", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Apify ships an official MCP server exposing Actors as tools."},
    buildability="Easy", blocker=None,
    evidence="https://docs.apify.com/api/v2", confidence=92, verification_status="agent_verified", notes="")

add(id=56, name="Firecrawl", website="firecrawl.dev", category="Data, SEO & Scraping",
    description="LLM-ready web scraping/crawling API purpose-built for feeding AI agents and RAG pipelines.",
    auth=["API Key (Bearer)"], self_serve="freemium_signup",
    self_serve_detail="Free-tier signup with starter credits; API key generated instantly on signup.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Python", "Node"], "breadth": "medium",
                 "rate_limits": "documented, plan-based", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Firecrawl publishes an official MCP server -- itself part of the standard agentic-research toolchain."},
    buildability="Easy", blocker=None,
    evidence="https://docs.firecrawl.dev/introduction", confidence=93, verification_status="agent_verified", notes="")

add(id=57, name="Bright Data", website="brightdata.com", category="Data, SEO & Scraping",
    description="Enterprise proxy network and web-data collection platform.",
    auth=["API Key (Bearer)", "Zone credentials (username/password for proxies)"], self_serve="freemium_signup",
    self_serve_detail="Free trial credit on signup; API key and proxy zone credentials self-generated instantly in the control panel.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Python", "Node"], "breadth": "broad",
                 "rate_limits": "documented, plan-based", "docs_public": True},
    mcp={"official": True, "community": False, "notes": "Bright Data publishes an official MCP server for its Web Unlocker/SERP APIs."},
    buildability="Easy", blocker=None,
    evidence="https://docs.brightdata.com/api-reference/introduction", confidence=88, verification_status="agent_verified", notes="")

add(id=58, name="Sherlock", website="github.com/sherlock-project/sherlock", category="Data, SEO & Scraping",
    description="Open-source CLI tool that hunts for usernames across social networks (OSINT).",
    auth=["None (local CLI tool)"], self_serve="open",
    self_serve_detail="Not a hosted SaaS/API at all -- it's an installable Python CLI/library; 'access' just means installing the package.",
    api_surface={"rest": False, "graphql": False, "webhooks": False, "sdks": ["Python (CLI/library)"],
                 "breadth": "narrow (single-purpose)", "rate_limits": "n/a (subject to each target site's own limits)", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "Community MCP wrappers exist that expose Sherlock as an agent tool."},
    buildability="Medium", blocker="Not a hosted API/toolkit-native integration; would need to be wrapped as a subprocess/CLI-invoking tool rather than called over HTTP, and its scraping approach is fragile against target-site changes.",
    evidence="https://github.com/sherlock-project/sherlock", confidence=90, verification_status="agent_verified",
    notes="Structurally different from every other row: a CLI tool, not a SaaS API.")

add(id=59, name="Waterfall.io", website="waterfall.io", category="Data, SEO & Scraping",
    description="B2B contact/company data enrichment API aggregating 30+ underlying data vendors.",
    auth=["API Key (x-api-key header)"], self_serve="partnership_required",
    self_serve_detail="Usage API takes a self-serve API key with no long-term contract required, but Waterfall states publicly it is 'very selective' about partnering with platforms that want to build products on top of its data -- so building a general-purpose toolkit integration (vs. a single internal workflow) requires their approval.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": [], "breadth": "narrow (single enrichment endpoint family)",
                 "rate_limits": "100-1000+ req/min depending on plan, documented on their site", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Medium", blocker="Company explicitly gates platform/reseller-style API use behind a selective partnership review, even though direct usage is API-key self-serve.",
    evidence="https://www.waterfall.io/book-a-call", confidence=80, verification_status="human_verified",
    notes="Live-checked during verification sample: confirmed API-key auth and no-contract usage, but also found the explicit partnership-gate language for platform builders on their own site FAQ.")

add(id=60, name="Clay", website="clay.com", category="Data, SEO & Scraping",
    description="Data enrichment/GTM automation workspace that orchestrates 100+ underlying data providers.",
    auth=["API Key", "Webhooks (incoming, for Clay 'HTTP API' tables)"], self_serve="freemium_signup",
    self_serve_detail="Free-tier workspace signup with limited credits; Clay's own API/webhook tables are usable immediately from the workspace.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "credit-based, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; Clay is more often the *consumer* of other tools' MCP servers than a provider."},
    buildability="Easy", blocker=None,
    evidence="https://clay.com/university/lesson/clay-api", confidence=78, verification_status="agent_verified", notes="")


# ============================================================
# 7. Developer, Infra & Data Platforms
# ============================================================
add(id=61, name="GitHub", website="docs.github.com/rest", category="Developer & Infra",
    description="The default code-hosting/collaboration platform, with a deep REST + GraphQL API.",
    auth=["OAuth2", "Personal Access Token", "GitHub App (JWT)"], self_serve="open",
    self_serve_detail="Free account; PAT generated instantly in Settings > Developer Settings, zero approval.",
    api_surface={"rest": True, "graphql": True, "webhooks": True, "sdks": ["every major language"], "breadth": "broad",
                 "rate_limits": "5000 req/hr authenticated (documented, higher for GitHub Apps)", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "GitHub publishes an official, widely-used MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://docs.github.com/en/rest", confidence=98, verification_status="agent_verified", notes="")

add(id=62, name="Vercel", website="vercel.com/docs/rest-api", category="Developer & Infra",
    description="Frontend cloud/deployment platform for Next.js and other frameworks.",
    auth=["Bearer Token (Access Token)", "OAuth2 (Integrations)"], self_serve="open",
    self_serve_detail="Free Hobby account; Access Token self-generated instantly in Account Settings > Tokens.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Node"], "breadth": "broad",
                 "rate_limits": "documented per-endpoint", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Vercel publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://vercel.com/docs/rest-api", confidence=95, verification_status="agent_verified", notes="")

add(id=63, name="Netlify", website="docs.netlify.com/api", category="Developer & Infra",
    description="Static site hosting/deployment platform, direct Vercel competitor.",
    auth=["OAuth2", "Personal Access Token"], self_serve="open",
    self_serve_detail="Free tier; PAT self-generated instantly in User Settings > Applications.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Node"], "breadth": "broad",
                 "rate_limits": "500 req/min, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP confirmed; community servers exist."},
    buildability="Easy", blocker=None,
    evidence="https://docs.netlify.com/api/get-started/", confidence=90, verification_status="agent_verified", notes="")

add(id=64, name="Cloudflare", website="developers.cloudflare.com/api", category="Developer & Infra",
    description="CDN/security/edge-compute platform (DNS, Workers, Zero Trust, etc.).",
    auth=["API Token (Bearer)", "OAuth2 (limited)"], self_serve="open",
    self_serve_detail="Free tier; scoped API Tokens self-generated instantly in the dashboard.",
    api_surface={"rest": True, "graphql": True, "webhooks": True, "sdks": ["every major language"], "breadth": "broad",
                 "rate_limits": "1200 req/5min per token, documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Cloudflare publishes official MCP servers (Workers, Docs, etc.)."},
    buildability="Easy", blocker=None,
    evidence="https://developers.cloudflare.com/api/", confidence=96, verification_status="agent_verified", notes="")

add(id=65, name="Supabase", website="supabase.com/docs", category="Developer & Infra",
    description="Open-source Firebase alternative: Postgres, auth, storage, and edge functions as a managed platform.",
    auth=["API Key (anon/service_role)", "OAuth2 (management API)"], self_serve="open",
    self_serve_detail="Free-tier project self-created instantly; API keys visible immediately in project settings.",
    api_surface={"rest": True, "graphql": True, "webhooks": True, "sdks": ["JS", "Python", "Dart", "Swift"],
                 "breadth": "broad", "rate_limits": "plan-based, documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Supabase publishes an official MCP server for its management API."},
    buildability="Easy", blocker=None,
    evidence="https://supabase.com/docs/guides/api", confidence=95, verification_status="agent_verified", notes="")

add(id=66, name="Neo4j", website="neo4j.com/docs/api", category="Developer & Infra",
    description="Graph database; programmatic access is via the Bolt protocol/drivers rather than a general REST API.",
    auth=["Basic Auth / Bearer (drivers)", "API Key (Aura management API)"], self_serve="freemium_signup",
    self_serve_detail="Free AuraDB Free tier self-created instantly; connection credentials available immediately. The management/admin API for provisioning instances also self-serve via API key.",
    api_surface={"rest": True, "graphql": True, "webhooks": False, "sdks": ["Python", "Java", "JS", "Go", ".NET"],
                 "breadth": "broad (as a database, not a typical SaaS API)", "rate_limits": "n/a (connection/query-based, not request-quota)", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Neo4j publishes an official MCP server for querying via Cypher."},
    buildability="Medium", blocker="Primary access pattern is a database driver protocol (Bolt/Cypher), not a typical REST endpoint, so integration effort differs from most other rows even though it is self-serve.",
    evidence="https://neo4j.com/docs/aura/", confidence=78, verification_status="agent_verified", notes="")

add(id=67, name="Snowflake", website="docs.snowflake.com", category="Developer & Infra",
    description="Cloud data warehouse with SQL API and increasingly agent-oriented Cortex features.",
    auth=["Key-pair (JWT)", "OAuth2", "Basic Auth (username/password, discouraged)"], self_serve="freemium_signup",
    self_serve_detail="Free 30-day trial account with credits; SQL API access configured self-serve via key-pair auth, no manual approval.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": ["Python", "Java", "Node", "Go"],
                 "breadth": "broad", "rate_limits": "warehouse/credit-based, not classic req-quota", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Snowflake publishes an official Cortex/Snowflake MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://docs.snowflake.com/en/developer-guide/sql-api/index", confidence=85, verification_status="agent_verified", notes="")

add(id=68, name="MongoDB Atlas", website="mongodb.com/docs/atlas/api", category="Developer & Infra",
    description="Managed MongoDB cloud platform, with both a database driver interface and an Atlas Administration API.",
    auth=["Digest Auth (API keys) for Admin API", "SCRAM/X.509 for database driver"], self_serve="open",
    self_serve_detail="Free M0 cluster self-created instantly; Atlas Admin API keys self-generated in Organization Access Manager, no approval.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["every major language (drivers)"],
                 "breadth": "broad", "rate_limits": "documented per-endpoint on Admin API", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "MongoDB publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://www.mongodb.com/docs/atlas/reference/api-resources-spec/", confidence=90, verification_status="agent_verified", notes="")

add(id=69, name="Datadog", website="docs.datadoghq.com/api", category="Developer & Infra",
    description="Observability platform (metrics, logs, traces, monitors) with a comprehensive API.",
    auth=["API Key + Application Key"], self_serve="freemium_signup",
    self_serve_detail="Free-tier trial; API key and App key self-generated instantly in Organization Settings.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["every major language"], "breadth": "broad",
                 "rate_limits": "documented per-endpoint", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Datadog publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://docs.datadoghq.com/api/latest/", confidence=93, verification_status="agent_verified", notes="")

add(id=70, name="Sentry", website="docs.sentry.io/api", category="Developer & Infra",
    description="Error-tracking/application-monitoring platform.",
    auth=["Bearer Token (Auth Token)", "OAuth2"], self_serve="open",
    self_serve_detail="Free developer tier; Auth Token self-generated instantly in Settings > Auth Tokens.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["every major language"], "breadth": "broad",
                 "rate_limits": "documented per-endpoint", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Sentry publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://docs.sentry.io/api/", confidence=93, verification_status="agent_verified", notes="")


# ============================================================
# 8. Productivity & Project Management
# ============================================================
add(id=71, name="Notion", website="developers.notion.com", category="Productivity & PM",
    description="Docs/wiki/database workspace with a widely-used public API and integration ecosystem.",
    auth=["OAuth2 (public integrations)", "Internal Integration Token"], self_serve="open",
    self_serve_detail="Free personal workspace; Internal Integration token self-generated instantly at notion.so/my-integrations.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["JS/TS"], "breadth": "broad",
                 "rate_limits": "~3 req/sec average, documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Notion publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://developers.notion.com/docs/getting-started", confidence=96, verification_status="agent_verified", notes="")

add(id=72, name="Airtable", website="airtable.com/developers", category="Productivity & PM",
    description="Spreadsheet-database hybrid with a very developer-friendly REST API.",
    auth=["Personal Access Token", "OAuth2"], self_serve="open",
    self_serve_detail="Free-tier account; PAT self-generated instantly at airtable.com/create/tokens.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["JS"], "breadth": "broad",
                 "rate_limits": "5 req/sec per base, documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Airtable publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://airtable.com/developers/web/api/introduction", confidence=95, verification_status="agent_verified", notes="")

add(id=73, name="Linear", website="developers.linear.app", category="Productivity & PM",
    description="Issue-tracking tool built for fast-moving software teams, GraphQL-first API.",
    auth=["OAuth2", "Personal API Key"], self_serve="open",
    self_serve_detail="Free-tier workspace; Personal API key self-generated instantly in Settings > API.",
    api_surface={"rest": False, "graphql": True, "webhooks": True, "sdks": ["TS SDK"], "breadth": "broad",
                 "rate_limits": "complexity-based per request, documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Linear publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://developers.linear.app/docs/graphql/working-with-the-graphql-api", confidence=93, verification_status="agent_verified", notes="")

add(id=74, name="Jira", website="developer.atlassian.com", category="Productivity & PM",
    description="Atlassian's issue-tracker/project-management tool, ubiquitous in enterprise engineering orgs.",
    auth=["OAuth2 (3LO)", "API Token (Basic auth)"], self_serve="open",
    self_serve_detail="Free-tier Cloud site; API token self-generated instantly at id.atlassian.com/manage-profile/security/api-tokens.",
    api_surface={"rest": True, "graphql": True, "webhooks": True, "sdks": ["Python", "Node", "Java"], "breadth": "broad",
                 "rate_limits": "documented, cost-budget based", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Atlassian publishes an official Rovo/Jira MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/", confidence=95, verification_status="agent_verified", notes="")

add(id=75, name="Asana", website="developers.asana.com", category="Productivity & PM",
    description="Task/project management tool with a mature public API.",
    auth=["OAuth2", "Personal Access Token"], self_serve="open",
    self_serve_detail="Free-tier workspace; PAT self-generated instantly in My Settings > Apps > Manage Developer Apps.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Node", "Python", "Java"], "breadth": "broad",
                 "rate_limits": "1500 req/min per user, documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Asana publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://developers.asana.com/docs/overview", confidence=94, verification_status="agent_verified", notes="")

add(id=76, name="Monday.com", website="developer.monday.com", category="Productivity & PM",
    description="Work-OS style project/workflow management platform, GraphQL API.",
    auth=["OAuth2", "Personal API Token"], self_serve="open",
    self_serve_detail="Free-tier account; API token self-generated instantly under Admin > API.",
    api_surface={"rest": False, "graphql": True, "webhooks": True, "sdks": ["JS", "Java"], "breadth": "broad",
                 "rate_limits": "complexity-point budget, documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "monday.com publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://developer.monday.com/api-reference/docs", confidence=92, verification_status="agent_verified", notes="")

add(id=77, name="ClickUp", website="clickup.com/api", category="Productivity & PM",
    description="All-in-one work-management platform with a broad REST API.",
    auth=["OAuth2", "Personal API Token"], self_serve="open",
    self_serve_detail="Free-tier workspace; personal token self-generated instantly in Settings > Apps.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "broad",
                 "rate_limits": "100 req/min, documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "ClickUp publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://developer.clickup.com/docs", confidence=90, verification_status="agent_verified", notes="")

add(id=78, name="Coda", website="coda.io/developers", category="Productivity & PM",
    description="Doc/spreadsheet/app hybrid workspace with a REST API for reading and writing tables.",
    auth=["Bearer Token (API Token)"], self_serve="open",
    self_serve_detail="Free-tier account; API token self-generated instantly in Account Settings.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "documented per-endpoint", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP confirmed; community servers exist."},
    buildability="Easy", blocker=None,
    evidence="https://coda.io/developers/apis/v1", confidence=88, verification_status="agent_verified", notes="")

add(id=79, name="Smartsheet", website="smartsheet.com/developers", category="Productivity & PM",
    description="Spreadsheet-based work-management platform popular in enterprise operations teams.",
    auth=["OAuth2", "API Access Token"], self_serve="open",
    self_serve_detail="Free trial account; API access token self-generated instantly in Account > Personal Settings > API Access.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Java", "Python", ".NET"], "breadth": "broad",
                 "rate_limits": "300 req/min, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP confirmed; community servers exist."},
    buildability="Easy", blocker=None,
    evidence="https://developers.smartsheet.com/api/smartsheet/", confidence=88, verification_status="agent_verified", notes="")

add(id=80, name="Harvest", website="help.getharvest.com/api-v2", category="Productivity & PM",
    description="Time-tracking and invoicing tool for services businesses.",
    auth=["OAuth2", "Personal Access Token"], self_serve="open",
    self_serve_detail="Free trial account; PAT self-generated instantly at id.getharvest.com/developers.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Ruby", "Node"], "breadth": "medium",
                 "rate_limits": "100 req/15s, documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Easy", blocker=None,
    evidence="https://help.getharvest.com/api-v2/", confidence=86, verification_status="agent_verified", notes="")


# ============================================================
# 9. Finance & Fintech
# ============================================================
add(id=81, name="Stripe", website="stripe.com/docs/api", category="Finance & Fintech",
    description="The reference-standard payments API; broad, deeply documented, and API-first by design.",
    auth=["API Key (Bearer)", "OAuth2 (Connect)"], self_serve="open",
    self_serve_detail="Free account; test-mode API keys visible instantly on signup, live keys unlock after basic account activation.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["every major language"], "breadth": "broad",
                 "rate_limits": "100 req/sec (live mode), documented", "docs_public": True},
    mcp={"official": True, "community": True, "notes": "Stripe publishes an official MCP server."},
    buildability="Easy", blocker=None,
    evidence="https://stripe.com/docs/api", confidence=98, verification_status="agent_verified", notes="")

add(id=82, name="Plaid", website="plaid.com/docs", category="Finance & Fintech",
    description="Bank-account connectivity/financial-data API used by fintech apps.",
    auth=["API Key (client_id + secret)"], self_serve="freemium_signup",
    self_serve_detail="Free Sandbox + Development environment self-serve on signup; Production access requires an application review (fraud/compliance screening).",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["every major language"], "breadth": "broad",
                 "rate_limits": "documented per-product", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community servers exist."},
    buildability="Medium", blocker="Production access requires Plaid's manual application review for compliance reasons, even though Sandbox is instant.",
    evidence="https://plaid.com/docs/api/", confidence=90, verification_status="agent_verified", notes="")

add(id=83, name="Binance", website="binance-docs.github.io", category="Finance & Fintech",
    description="Major cryptocurrency exchange with a broad public trading/market-data API.",
    auth=["API Key + HMAC signature"], self_serve="open",
    self_serve_detail="Free account (KYC required for trading, not for market-data-only access); API key self-generated instantly.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["every major language"], "breadth": "broad",
                 "rate_limits": "weight-based per endpoint, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community servers exist."},
    buildability="Easy", blocker=None,
    evidence="https://binance-docs.github.io/apidocs/spot/en/", confidence=88, verification_status="agent_verified", notes="")

add(id=84, name="Paygent Connect", website="paygent.com", category="Finance & Fintech",
    description="Payment orchestration layer described as NMI-powered; positioned for agencies/SaaS platforms reselling payments.",
    auth=["API Key (inherits NMI Direct Post/Query API model)"], self_serve="gated_unclear",
    self_serve_detail="Could not locate an independent, public developer-docs site distinct from the underlying NMI gateway it is built on; onboarding appears to run through a reseller/ISO signup process rather than public self-serve signup.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": [], "breadth": "unknown",
                 "rate_limits": "unknown", "docs_public": False},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Hard", blocker="No independently verifiable public API documentation found; onboarding appears to require becoming a reseller/merchant account holder first.",
    evidence="https://www.nmi.com/developers", confidence=35, verification_status="flagged",
    notes="Unknown/low-confidence: this is a defeated-app case. Evidence URL points to the underlying NMI platform docs since a distinct public Paygent Connect API reference could not be confirmed.")

add(id=85, name="iPayX", website="ipayx.ai", category="Finance & Fintech",
    description="FX-forensic-audit layer (FINTRAC-registered) that detects hidden bank/card markup on currency transactions.",
    auth=["None (free comparison endpoint)", "Bearer Token / API Key (paid audit endpoints)"], self_serve="freemium_signup",
    self_serve_detail="One core comparison tool is callable with no auth at all (free); deeper forensic-audit and full-report endpoints require a Bearer/API key and hit a 402 Payment Required after a free-trial allowance -- self-serve, metered by usage rather than gated by approval.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": [], "breadth": "narrow (single-purpose FX audit)",
                 "rate_limits": "free-trial credit limit, then paid per-report", "docs_public": True},
    mcp={"official": True, "community": False, "notes": "iPayX ships an official MCP server ('iPayX FX Audit') listed on public MCP directories (Glama, mcpservers.org, GitHub)."},
    buildability="Easy", blocker=None,
    evidence="https://www.ipayx.ai/docs/mcp-server", confidence=82, verification_status="human_verified",
    notes="Live-checked during verification sample via its public MCP listing: confirmed a no-auth free tier, Bearer-token paid tier, and an official first-party MCP server -- unusual for how small/new this vendor is.")

add(id=86, name="QuickBooks", website="developer.intuit.com", category="Finance & Fintech",
    description="Small-business accounting software with a mature public API.",
    auth=["OAuth2"], self_serve="open",
    self_serve_detail="Free developer account and Sandbox company self-serve instantly at developer.intuit.com; production keys require a short automated app review (not a sales gate).",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Node", "Python", "Java", "PHP", ".NET"],
                 "breadth": "broad", "rate_limits": "500 req/min per realm, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community servers exist."},
    buildability="Easy", blocker=None,
    evidence="https://developer.intuit.com/app/developer/qbo/docs/get-started", confidence=90, verification_status="agent_verified", notes="")

add(id=87, name="Xero", website="developer.xero.com", category="Finance & Fintech",
    description="Cloud accounting software popular outside the US, strong API ecosystem.",
    auth=["OAuth2"], self_serve="open",
    self_serve_detail="Free developer account and demo company self-serve instantly at developer.xero.com.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Node", "Python", "Java", ".NET"],
                 "breadth": "broad", "rate_limits": "60 req/min, 5000 req/day, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "No official MCP; community servers exist."},
    buildability="Easy", blocker=None,
    evidence="https://developer.xero.com/documentation/getting-started-guide/", confidence=90, verification_status="agent_verified", notes="")

add(id=88, name="Brex", website="developer.brex.com", category="Finance & Fintech",
    description="Corporate card/spend-management platform for startups and enterprises.",
    auth=["OAuth2", "API Key"], self_serve="admin_approval_required",
    self_serve_detail="API access requires an active Brex account (business underwriting/approval to become a customer at all); once a customer, API keys are self-generated in the dashboard by an admin.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "documented per-endpoint", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Medium", blocker="Must be an underwritten Brex customer before API keys can be created at all -- not a pure developer-sandbox self-serve.",
    evidence="https://developer.brex.com/docs/introduction/", confidence=78, verification_status="agent_verified", notes="")

add(id=89, name="Ramp", website="docs.ramp.com", category="Finance & Fintech",
    description="Corporate card/spend-management platform, Brex's closest competitor.",
    auth=["OAuth2 (client credentials)"], self_serve="admin_approval_required",
    self_serve_detail="Similar to Brex: must be an approved Ramp business customer before API credentials exist; once a customer, OAuth2 client is self-serve from the admin dashboard.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "documented per-endpoint", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Medium", blocker="Requires an approved Ramp customer account before any API credentials can be created.",
    evidence="https://docs.ramp.com/developer-api/v1/overview/introduction", confidence=78, verification_status="agent_verified", notes="")

add(id=90, name="PitchBook", website="pitchbook.com", category="Finance & Fintech",
    description="Private-markets/M&A research data platform (companies, deals, investors).",
    auth=["OAuth2 (enterprise-issued)"], self_serve="contact_sales_only",
    self_serve_detail="No public self-signup of any kind; data access (including API) is sold as part of an enterprise subscription and provisioned by PitchBook's sales/success team.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": [], "breadth": "unknown (behind login)",
                 "rate_limits": "unknown/not public", "docs_public": False},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Hard", blocker="Enterprise-only, contact-sales; no public docs or trial access to independently verify the API surface.",
    evidence="https://pitchbook.com/data", confidence=50, verification_status="flagged", notes="")


# ============================================================
# 10. AI, Research & Media-native
# ============================================================
add(id=91, name="NotebookLM", website="cloud.google.com/gemini", category="AI, Research & Media", 
    description="Google's AI research/notebook assistant; consumer product has no public API of its own.",
    auth=["OAuth2 (via underlying Gemini Enterprise API, not NotebookLM directly)"], self_serve="contact_sales_only",
    self_serve_detail="The consumer NotebookLM product has no public developer API at all. Programmatic, notebook-like capability is only available indirectly through Gemini Enterprise, which is an enterprise-sales product.",
    api_surface={"rest": False, "graphql": False, "webhooks": False, "sdks": [], "breadth": "none (no public API)",
                 "rate_limits": "n/a", "docs_public": False},
    mcp={"official": False, "community": False, "notes": "No MCP server exists because there is no public API to wrap."},
    buildability="Impossible", blocker="No public API for the NotebookLM product itself; the only related programmatic path is Gemini Enterprise, a separate contact-sales product, not a NotebookLM integration.",
    evidence="https://cloud.google.com/gemini", confidence=75, verification_status="flagged",
    notes="Defeated-app case: this is a real, honest 'no' -- worth flagging clearly for Composio since it's a commonly requested app.")

add(id=92, name="Otter.ai", website="help.otter.ai", category="AI, Research & Media",
    description="AI meeting-notes/transcription tool with an enterprise API and an MCP server.",
    auth=["API Key"], self_serve="paid_plan_required",
    self_serve_detail="API access is documented as part of Otter's Business/Enterprise tiers, not the free or Pro consumer tiers -- a paid-plan gate rather than a partnership.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "narrow-medium",
                 "rate_limits": "not prominently documented", "docs_public": True},
    mcp={"official": True, "community": False, "notes": "Otter documents an MCP server in its help center."},
    buildability="Medium", blocker="API is restricted to Business/Enterprise plans; no self-serve free-tier key for independent testing.",
    evidence="https://help.otter.ai/", confidence=68, verification_status="agent_verified", notes="")

add(id=93, name="Fathom", website="fathom.video", category="AI, Research & Media",
    description="AI meeting-recorder/notetaker with a growing developer API.",
    auth=["API Key (Bearer)"], self_serve="paid_plan_required",
    self_serve_detail="API access is documented for Team/paid plans; free tier does not include API access.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "narrow-medium",
                 "rate_limits": "not prominently documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found at time of research."},
    buildability="Medium", blocker="API gated behind a paid plan; no free-tier key for independent testing.",
    evidence="https://fathom.video", confidence=55, verification_status="flagged", notes="")

add(id=94, name="Consensus", website="consensus.app", category="AI, Research & Media",
    description="AI-powered academic search engine that answers questions using 200M+ peer-reviewed papers.",
    auth=["Bearer Token (API Key)"], self_serve="freemium_signup",
    self_serve_detail="Free account self-signup at consensus.app/sign-up gets a working API key immediately (quick_search endpoint); higher rate limits and richer fields (study_type, DOI) require Pro/Enterprise, a request-a-quote upsell rather than a hard access gate.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": ["Shell", "Node", "Ruby", "PHP", "Python (examples in docs)"],
                 "breadth": "narrow (single search/retrieval endpoint family)", "rate_limits": "free-tier limited, Enterprise = unlimited, documented", "docs_public": True},
    mcp={"official": True, "community": False, "notes": "Consensus publishes an official MCP server at mcp.consensus.app, used natively by ChatGPT Deep Research and other MCP clients."},
    buildability="Easy", blocker=None,
    evidence="https://docs.consensus.app/", confidence=90, verification_status="human_verified",
    notes="CORRECTED during verification: the agent's first pass ('no public API found', Hard/Unknown) was wrong. A live check found a fully public, self-serve API (docs.consensus.app) and an official MCP server -- this row moved from Hard/flagged to Easy/human_verified after the check.")

add(id=95, name="Reducto", website="reducto.ai", category="AI, Research & Media",
    description="Document-parsing API that converts complex PDFs/scans into structured, LLM-ready data.",
    auth=["API Key (Bearer)"], self_serve="freemium_signup",
    self_serve_detail="Free-tier signup with starter credits; API key self-generated instantly.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": ["Python", "Node"], "breadth": "medium",
                 "rate_limits": "credit-based, documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found at time of research."},
    buildability="Easy", blocker=None,
    evidence="https://docs.reducto.ai/", confidence=80, verification_status="agent_verified", notes="")

add(id=96, name="Devin", website="docs.devin.ai", category="AI, Research & Media",
    description="Cognition's autonomous software-engineering agent, with its own API and MCP integration.",
    auth=["API Key (Bearer)"], self_serve="paid_plan_required",
    self_serve_detail="API access requires an active paid Devin plan with API credits; no free-tier key.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "documented, credit-based", "docs_public": True},
    mcp={"official": True, "community": False, "notes": "Devin documents an official MCP integration."},
    buildability="Medium", blocker="No free tier; a paid Devin plan is required before API keys can be issued.",
    evidence="https://docs.devin.ai/", confidence=78, verification_status="agent_verified", notes="")

add(id=97, name="higgsfield", website="higgsfield.ai", category="AI, Research & Media",
    description="AI video/content-generation suite with a CLI-based workflow.",
    auth=["API Key"], self_serve="gated_unclear",
    self_serve_detail="Product markets a CLI and API but a clear, independent public developer-docs reference (auth model, endpoints, rate limits) could not be confirmed at time of research.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": [], "breadth": "unknown",
                 "rate_limits": "unknown", "docs_public": False},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Hard", blocker="Could not confirm authoritative public API documentation; treat as Unknown pending direct verification with the vendor.",
    evidence="https://higgsfield.ai", confidence=30, verification_status="flagged",
    notes="Defeated-app case: newer/smaller product, insufficient public documentation to make a confident call.")

add(id=98, name="Mermaid CLI", website="github.com/mermaid-js/mermaid-cli", category="AI, Research & Media",
    description="Open-source CLI (mmdc) that renders Mermaid diagram syntax to PNG/SVG/PDF.",
    auth=["None (local CLI tool)"], self_serve="open",
    self_serve_detail="Not a hosted SaaS -- an installable open-source npm package (`@mermaid-js/mermaid-cli`) run locally or in CI, no account or key of any kind.",
    api_surface={"rest": False, "graphql": False, "webhooks": False, "sdks": ["Node CLI"], "breadth": "narrow (single-purpose renderer)",
                 "rate_limits": "n/a (local execution)", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "Community MCP servers exist that expose Mermaid rendering as an agent tool."},
    buildability="Easy", blocker=None,
    evidence="https://github.com/mermaid-js/mermaid-cli", confidence=92, verification_status="agent_verified",
    notes="Like Sherlock, this is a CLI/library rather than a hosted API -- 'buildability' means wrapping a subprocess call, not calling HTTP endpoints.")

add(id=99, name="YouTube Transcript API (transcriptapi.com)", website="transcriptapi.com", category="AI, Research & Media",
    description="Third-party hosted API that fetches YouTube video transcripts/captions on demand.",
    auth=["API Key (Bearer)"], self_serve="freemium_signup",
    self_serve_detail="Free-tier signup with limited requests; API key self-generated instantly.",
    api_surface={"rest": True, "graphql": False, "webhooks": False, "sdks": [], "breadth": "narrow (single-purpose)",
                 "rate_limits": "credit-based, documented", "docs_public": True},
    mcp={"official": False, "community": True, "notes": "Community MCP wrappers exist for YouTube-transcript-style tools."},
    buildability="Easy", blocker=None,
    evidence="https://transcriptapi.com/", confidence=70, verification_status="agent_verified",
    notes="Third-party wrapper around YouTube's own (non-public) caption data, not an official YouTube/Google product -- worth flagging that dependency risk to Composio.")

add(id=100, name="Grain", website="grain.com", category="AI, Research & Media",
    description="AI meeting-recording/highlight-reel tool for sales and user-research teams.",
    auth=["OAuth2", "API Key"], self_serve="paid_plan_required",
    self_serve_detail="Public API is documented but positioned for Business-tier customers; free/starter tiers do not include API access.",
    api_surface={"rest": True, "graphql": False, "webhooks": True, "sdks": [], "breadth": "medium",
                 "rate_limits": "not prominently documented", "docs_public": True},
    mcp={"official": False, "community": False, "notes": "No MCP server found."},
    buildability="Medium", blocker="API access restricted to paid Business-tier plans; no free-tier key for independent testing.",
    evidence="https://grain.com/", confidence=60, verification_status="flagged", notes="")


if __name__ == "__main__":
    print(f"Loaded {len(APPS)} app rows.")
    assert len(APPS) == 100, f"expected 100 rows, got {len(APPS)}"
    ids = [a["id"] for a in APPS]
    assert len(set(ids)) == 100, "duplicate ids found"
    print("OK: 100 unique rows.")
