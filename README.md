# VendorGuard AI

VendorGuard AI is a human-governed, evidence-first vendor risk assessment application
built for the Kaggle 5-Day AI Agents Intensive capstone.

## Course concepts demonstrated

- Google Agent Development Kit multi-agent workflow
- Model Context Protocol policy server
- Agent Skills
- Prompt-injection defence
- Human-in-the-loop approval
- Deterministic and semantic evaluation design
- Cloud Run-ready deployment
- Audit logs and structured outputs

## Architecture

```text
React UI
   |
FastAPI API
   |
Assessment workflow
   |-- Evidence agent
   |-- Risk and security agent
   |-- Policy agent / MCP tools
   |-- Decision and report agent
   |
Human approval gate
   |
SQLite locally / PostgreSQL upgrade path
```

The local API runs in deterministic demonstration mode without an API key. The ADK agent
definitions are included under `backend/app/agents/` and can be run after adding a Gemini key.

## Requirements

- Python 3.10+
- Node.js 20+
- npm
- Optional: Gemini API key for ADK mode

## Backend setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
uvicorn app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000/docs`.

## Frontend setup

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Tests

Run:

```powershell
cd backend
pytest -q
```

## MCP server

```powershell
python mcp_server\server.py
```

The server uses MCP stdio transport and exposes policy lookup tools.

## ADK development

Add `GEMINI_API_KEY` to a local `.env` file, then:

```powershell
cd backend
adk web
```

Select the `app.agents` package if requested. The ADK root agent is defined in
`backend/app/agents/agent.py`.

## Demo vendors

- CloudNova: low-risk, comparatively complete evidence
- PaySphere: medium-risk payment provider with missing controls
- DataQuick: high-risk PII processor containing contradictory claims and a prompt injection

## Cloud Run

Build and deploy from the repository root with the included Dockerfile, or use a
dedicated Cloud Build configuration. For the first local container test:

```powershell
docker compose up --build
```

Before a public deployment, configure the Cloud Run service, database and secrets in your
own Google Cloud project and verify the final container command and region.

Set environment variables through Cloud Run or Secret Manager. Do not place secrets in the image.

## Important limitation

VendorGuard is a demonstration decision-support tool. It does not certify real organisations
or replace legal, procurement, compliance or security professionals.
