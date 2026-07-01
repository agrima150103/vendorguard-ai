# Scalability Plan

## Local demonstration
One FastAPI process, SQLite and three synthetic vendors.

## L3 deployment
Cloud Run API with stateless request handling, Cloud SQL PostgreSQL, protected MCP service,
Secret Manager and central logs.

## Capacity model

Let:
- A = assessments per minute
- C = average concurrent model calls per assessment
- T = average model-call duration in seconds

Expected model-call concurrency is approximately:

`concurrency = A × C × T / 60`

For example, 20 assessments/minute, 4 calls/assessment and 5 seconds/call gives
approximately 6.7 concurrent model calls. Configure Cloud Run concurrency and maximum
instances after measured load tests rather than using this estimate as a production claim.

## L4 criteria

The project becomes L4 only after supporting actual users and documenting:
traffic, latency percentiles, error rate, scaling events, user feedback and operational cost.
