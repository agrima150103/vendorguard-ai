# 🛡️ VendorGuard AI

### Human-Governed Multi-Agent Vendor Risk Assessment

**Evidence first. Agents recommend. Humans decide.**

VendorGuard AI is an evidence-first vendor risk assessment platform built with **Google ADK, Model Context Protocol, FastAPI, and React**.

It separates evidence extraction, security analysis, policy enforcement, and decision generation across specialized agents while keeping high-risk decisions behind an explicit human approval gate.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-VendorGuard-2DD4A7?style=flat-square)](https://vendorguard-web.web.app/)
[![Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/agcodes0315/vendorguard-ai)
[![Google AI Agents](https://img.shields.io/badge/Google-AI%20Agents%20Intensive-4285F4?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/profile/badges/events/cloud/five-day-ai-agents)

`Google ADK` `MCP` `FastAPI` `React` `Human-in-the-Loop` `pytest` `Docker`

## 🚀 What VendorGuard Does

Vendor reviews often involve incomplete questionnaires, conflicting security claims, policy requirements, and evidence spread across multiple documents.

Using a single LLM to read everything and directly approve or reject a vendor creates a governance problem.

VendorGuard breaks the process into controlled stages:

1. Extract vendor claims and supporting evidence
2. Analyze security weaknesses and contradictions
3. Check findings against governed policy
4. Generate a structured recommendation
5. Escalate high-risk outcomes for human review
6. Record the final decision and supporting evidence

A recommendation is never treated as automatic authorization.

## 🖥️ Application

<img src="docs/assets/vendorguard-dashboard.png"
     alt="VendorGuard AI assessment dashboard"
     width="100%">

The dashboard provides a single view of vendor evidence, risk findings, policy results, recommendations, approval state, and audit history.

## 🧠 Multi-Agent Workflow

VendorGuard uses four agents with separate responsibilities.

| Agent | Responsibility |
|---|---|
| **Evidence Agent** | Extracts vendor claims and ties findings to supporting evidence |
| **Risk & Security Agent** | Identifies weaknesses, missing controls, and contradictory claims |
| **Policy Agent** | Evaluates findings against deterministic policy rules exposed through MCP |
| **Decision Agent** | Produces a structured, non-binding recommendation |

The overall flow is:

```text
Vendor Submission
       |
       v
Evidence Agent
       |
       v
Risk & Security Agent
       |
       v
Policy Agent
       |
       v
Decision Agent
       |
       v
Recommendation
       |
       v
Human Approval
       |
       v
Final Decision + Audit Record
```

## 🤝 Human-in-the-Loop Governance

VendorGuard deliberately separates **recommendation** from **authorization**.

For higher-risk assessments, the agent pipeline can recommend an outcome, but a human reviewer must approve or reject it before the final decision is recorded.

This prevents the AI layer from silently becoming the business decision-maker.

```text
Agent Recommendation
        |
        v
   Risk Evaluation
      /     \
     /       \
 Low Risk   High Risk
    |           |
    v           v
 Record      Human Review
                |
                v
          Final Decision
```

## 🔐 Prompt-Injection Defence

Vendor evidence is treated as untrusted input.

One synthetic vendor, `DataQuick`, intentionally contains an embedded prompt-injection attempt. The workflow is designed so that vendor-supplied instructions cannot override:

- system instructions
- policy rules
- agent responsibilities
- approval requirements
- audit behaviour

The adversarial behaviour is tested with `pytest`.

```bash
cd backend
pytest -q
```

The important distinction is that VendorGuard does not only look for suspicious text. The architecture prevents vendor-provided content from gaining authority over the workflow itself.

## 📋 Policy Enforcement with MCP

Policy evaluation is exposed through a dedicated **Model Context Protocol** server.

Run it with:

```bash
python mcp_server/server.py
```

This keeps two questions separate:

> What does the AI recommend?

and

> What does organizational policy permit?

The policy layer is deterministic rather than being left entirely to model interpretation.

## 🏢 Demo Vendors

Three synthetic vendors are included to make the assessment behaviour easy to reproduce.

| Vendor | Risk | Scenario |
|---|:---:|---|
| **CloudNova** | 🟢 Low | Comparatively complete evidence |
| **PaySphere** | 🟡 Medium | Missing controls and incomplete evidence |
| **DataQuick** | 🔴 High | Contradictory claims and prompt-injection content |

Using synthetic vendors keeps the demo reproducible and avoids making claims about real organizations.

## ⚙️ Key Engineering Features

| Capability | Implementation |
|---|---|
| Multi-agent orchestration | Google Agent Development Kit |
| Agent boundaries | Evidence, Risk, Policy, Decision |
| Policy enforcement | Model Context Protocol |
| Human review | Approval gate for high-risk outcomes |
| Prompt-injection handling | Untrusted evidence + adversarial tests |
| Evidence traceability | Source-backed findings |
| Auditability | Structured assessment history |
| API | FastAPI |
| Frontend | React |
| Local persistence | SQLite |
| Testing | pytest |
| Deployment | Firebase + Render |
| Offline/demo execution | Deterministic key-free fallback |

## 🧪 Evaluation and Testing

Testing focuses on the behaviour that matters most in an agentic risk system.

Current evaluation areas include:

- prompt-injection attempts
- contradictory vendor evidence
- unsupported claims
- missing evidence
- policy violations
- high-risk escalation
- approval enforcement
- deterministic fallback behaviour

Run the tests with:

```bash
cd backend
pytest -q
```

## 🧠 Google ADK Mode

The agent definitions live under:

```text
backend/app/agents/
```

The root ADK agent is defined in:

```text
backend/app/agents/agent.py
```

With a Gemini API key configured:

```bash
cd backend
adk web
```

VendorGuard can also run in a deterministic key-free mode so the core workflow remains demonstrable without external model credentials.

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | Google ADK |
| Policy Integration | Model Context Protocol |
| Backend | Python, FastAPI, Pydantic |
| Frontend | React, Vite |
| Model | Gemini |
| Local Database | SQLite |
| Production Database Path | PostgreSQL |
| Testing | pytest |
| Containerization | Docker |
| Frontend Hosting | Firebase Hosting |
| Backend Hosting | Render |

## 📁 Repository Structure

```text
vendorguard-ai/
├── backend/
│   └── app/
│       ├── agents/
│       ├── api/
│       ├── models/
│       └── services/
│
├── frontend/
│
├── mcp_server/
│
├── evaluations/
│
├── sample_data/
│
├── docs/
│   └── assets/
│
├── .github/
│   └── workflows/
│
├── Dockerfile
├── docker-compose.yml
├── render.yaml
└── README.md
```

## ⚙️ Running Locally

### Requirements

- Python 3.10+
- Node.js 20+
- npm
- Gemini API key for full ADK mode, optional

### 1. Clone the repository

```bash
git clone https://github.com/agcodes0315/vendorguard-ai.git
cd vendorguard-ai
```

### 2. Create the Python environment

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Start the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

### 6. Run tests

```bash
cd backend
pytest -q
```

### 7. Run with Docker

From the project root:

```bash
docker compose up --build
```

## ☁️ Deployment

VendorGuard is currently deployed using:

| Component | Service |
|---|---|
| Frontend | Firebase Hosting |
| Backend | Render |
| Containerization | Docker |

Live application:

**[Open VendorGuard AI](https://vendorguard-web.web.app/)**

The containerized backend can also be adapted for Cloud Run. Secrets and model credentials should be supplied through environment variables or a managed secret store rather than committed to the repository.

## 🎯 Design Decisions

### Evidence before conclusions

A finding should be connected to evidence rather than generated as an unsupported claim.

### Separate agent responsibilities

Evidence extraction, security analysis, policy enforcement, and recommendation generation remain separate.

### Policy is not an LLM opinion

Policy checks live outside the recommendation agent.

### Humans authorize higher-risk outcomes

Agents can support a decision. They do not silently finalize sensitive outcomes.

### External content is untrusted

Vendor documents never inherit system-level authority.

### Decisions should be reviewable

Evidence, findings, policy checks, recommendations, and final outcomes remain available for later review.

## 📌 What This Project Demonstrates

VendorGuard explores several problems that matter in production agentic systems:

- multi-agent orchestration
- agent responsibility boundaries
- Model Context Protocol integration
- evidence provenance
- prompt-injection resistance
- policy enforcement
- human-in-the-loop governance
- deterministic fallback behaviour
- API design
- full-stack deployment
- auditable decision workflows

## ⚠️ Scope

VendorGuard is a **decision-support and engineering demonstration system**.

It does not certify vendors and should not replace professional legal, procurement, compliance, cybersecurity, or risk-management review.

## 👩‍💻 Author

### Agrima Saxena

**Software Engineering · Applied AI · Multi-Agent Systems**

<table>
<tr>

<td width="60">
<a href="https://www.linkedin.com/in/agrima-saxena-142960426/" title="LinkedIn">
<img src="https://img.icons8.com/color/48/linkedin.png"
     width="32"
     height="32"
     alt="LinkedIn"/>
</a>
</td>

<td width="60">
<a href="mailto:agrimalc@gmail.com" title="Email">
<img src="https://img.icons8.com/color/48/gmail-new.png"
     width="32"
     height="32"
     alt="Email"/>
</a>
</td>

<td width="60">
<a href="https://github.com/agcodes0315" title="GitHub">
<img src="https://img.icons8.com/ios-glyphs/48/ffffff/github.png"
     width="32"
     height="32"
     alt="GitHub"/>
</a>
</td>

</tr>
</table>

<a href="https://vendorguard-web.web.app/">
<img src="https://img.shields.io/badge/Live%20Demo-Open%20VendorGuard-2DD4A7?style=flat-square"
     alt="VendorGuard Live Demo"/>
</a>

<a href="https://github.com/agcodes0315/vendorguard-ai">
<img src="https://img.shields.io/badge/GitHub-View%20Repository-181717?style=flat-square&logo=github&logoColor=white"
     alt="VendorGuard Repository"/>
</a>

<a href="https://developers.google.com/profile/badges/events/cloud/five-day-ai-agents">
<img src="https://img.shields.io/badge/Google-AI%20Agents%20Badge-4285F4?style=flat-square&logo=google&logoColor=white"
     alt="Google AI Agents Badge"/>
</a>

<br><br>

⭐ **If you found the architecture useful or interesting, consider starring the repository.**
