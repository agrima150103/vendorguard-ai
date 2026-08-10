<div align="center">

# VendorGuard AI

**Human-governed, evidence-first vendor risk assessment — built for the Kaggle × Google 5-Day AI Agents Intensive Capstone**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/agrima150103/vendorguard-ai)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-vendorguard--web-00C896?style=for-the-badge&logo=firebase)](https://vendorguard-web.web.app/)
[![Google Cloud Skills Badge](https://img.shields.io/badge/Google%20Cloud-5--Day%20AI%20Agents%20Badge-4285F4?style=for-the-badge&logo=googlecloud)](https://developers.google.com/profile/badges/events/cloud/five-day-ai-agents)

</div>

---

## Overview

VendorGuard AI is a multi-agent system that assesses vendor risk from submitted evidence — and refuses to let automation have the final word. Four specialized agents (Evidence, Risk & Security, Policy, Decision) built on the **Google Agent Development Kit** divide the work of extracting claims, scoring risk, checking policy, and drafting a recommendation. Every recommendation is **non-binding**: a human reviewer must approve the final decision before it's recorded, and every finding carries a source-backed evidence trail.

The project was built to demonstrate what "agents for business" should look like in practice — not just capable, but auditable, governed, and resistant to manipulation.

**Why it matters:** a single unverified or manipulated vendor claim shouldn't be able to steer a risk decision. VendorGuard treats every claim as something to be checked against evidence and policy, not taken at face value — and it caught this in testing: one demo vendor (`DataQuick`) contains an embedded prompt-injection attempt that the pipeline is designed to detect and flag rather than obey.

## How It Works

```
                         React UI
                            │
                       FastAPI API
                            │
                    Assessment Workflow
        ┌───────────────────┼───────────────────┐
        │                   │                   │
  Evidence Agent    Risk & Security Agent   Policy Agent (MCP)
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                   Decision & Report Agent
                            │
                   ── Human Approval Gate ──
                            │
              SQLite (local)  →  PostgreSQL (upgrade path)
```

1. **Evidence agent** — extracts and grounds vendor claims against submitted documentation
2. **Risk & security agent** — surfaces security findings and risk signals
3. **Policy agent** — checks findings against governed policy rules, exposed as tools via **MCP (Model Context Protocol)**
4. **Decision & report agent** — drafts a non-binding recommendation with full traceability
5. **Human review** — the only gate that can convert a recommendation into a recorded decision

## Key Capabilities

- **Evidence traceability** — every finding is linked back to its source claim; nothing is asserted without a trail
- **Governed policy checks** — five MCP-exposed tools enforce policy lookups deterministically, not by agent judgment
- **Human-in-the-loop approval** — agents recommend, only a human reviewer decides
- **Prompt-injection defence** — validated against three adversarial pytest scenarios, including a live embedded injection in the `DataQuick` demo vendor
- **Immutable audit logs** — a structured, per-assessment audit trail for every action taken
- **Deterministic demo mode** — runs locally without any API key; ADK/Gemini mode available for full agentic behavior

## Demo Vendors

| Vendor | Profile |
|---|---|
| **CloudNova** | Low-risk, comparatively complete evidence |
| **PaySphere** | Medium-risk payment provider with missing controls |
| **DataQuick** | High-risk PII processor with contradictory claims and an embedded prompt injection |

## Tech Stack

- **Frontend:** React (deployed on Firebase)
- **Backend:** FastAPI (deployed on Render)
- **Agents:** Google Agent Development Kit (ADK), built with Google Antigravity
- **Policy layer:** Model Context Protocol (MCP) server, stdio transport
- **Storage:** SQLite locally, with a PostgreSQL upgrade path
- **Testing:** pytest, including adversarial prompt-injection scenarios

## Getting Started

### Requirements
- Python 3.10+
- Node.js 20+
- npm
- *(Optional)* Gemini API key, for full ADK agent mode

### Backend
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
uvicorn app.main:app --reload --port 8000
```
Open **http://127.0.0.1:8000/docs**

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173**

### Tests
```bash
cd backend
pytest -q
```

### MCP Server
```bash
python mcp_server\server.py
```
Runs over MCP stdio transport and exposes the policy lookup tools.

### ADK / Agentic Mode
Add `GEMINI_API_KEY` to a local `.env` file, then:
```bash
cd backend
adk web
```
Select the `app.agents` package if prompted. The ADK root agent is defined in `backend/app/agents/agent.py`.

### Docker
```bash
docker compose up --build
```
For public deployment, configure the Cloud Run service, database, and secrets in your own Google Cloud project, and verify the container command and region before going live. Set environment variables through Cloud Run or Secret Manager — never place secrets in the image.

## Important Limitation

VendorGuard is a demonstration decision-support tool. It does **not** certify real organizations or replace legal, procurement, compliance, or security professionals.

---

<div align="center">
<sub>Every finding has evidence. Every action has permission. Every decision has a trace.</sub>
</div>