# Threat Model

## Primary threats

- Prompt injection in uploaded documents
- Secret leakage
- Tool over-permissioning
- Malformed model output
- Approval bypass
- PII leakage through logs
- Denial of service through oversized inputs

## Controls

- Untrusted-content boundary
- Pattern-based baseline detector plus model review
- Structured Pydantic validation
- Narrow tools
- Mandatory human state transition
- Environment variables and Secret Manager
- File type and size validation before real uploads are enabled
- Request IDs, timeouts and rate limits in production
