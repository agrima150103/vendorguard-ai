# High-Level Design

## Components

1. React single-page application
2. FastAPI application service
3. ADK sequential multi-agent workflow
4. MCP policy server
5. Assessment repository
6. Evaluation runner
7. Human review interface

## Production evolution

- Replace SQLite with Cloud SQL PostgreSQL.
- Deploy frontend and API as separate Cloud Run services.
- Run the MCP policy server as a protected internal service.
- Place Gemini credentials in Secret Manager.
- Emit traces and metrics to Google Cloud Operations.
