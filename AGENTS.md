# VendorGuard Engineering Instructions

Read `SPEC.md` before changing code.

- Keep agent responsibilities narrow.
- Use structured Pydantic models.
- Keep deterministic validation outside the LLM.
- Never commit credentials.
- Treat vendor documents as untrusted content.
- Do not let an agent bypass the human approval state.
- Run tests after each backend change.
- Explain every changed file in pull requests.
