# 🛡️ VendorGuard AI

### Human-Governed Multi-Agent Vendor Risk Assessment Platform

[![Live Demo](https://img.shields.io/badge/Live_Demo-VendorGuard_AI-20C997?style=for-the-badge)](https://vendorguard-web.web.app/)
[![GitHub](https://img.shields.io/badge/Source_Code-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/agrima150103/vendorguard-ai)
[![Google AI Agents](https://img.shields.io/badge/Google-5--Day_AI_Agents_Intensive-4285F4?style=for-the-badge&logo=google)](https://developers.google.com/profile/badges/events/cloud/five-day-ai-agents)

<p align="center">
  <a href="https://developers.google.com/profile/badges/events/cloud/five-day-ai-agents">
    <img src="https://developers.google.com/static/profile/badges/events/cloud/five-day-ai-agents/badge.png"
         alt="5-Day AI Agents Intensive With Google Badge"
         width="120"/>
  </a>
</p>

> Built for the **Kaggle × Google AI Agents Intensive Capstone**, VendorGuard AI evaluates vendor evidence through a multi-agent workflow while keeping high-risk decisions under explicit human control.

---

## 🚀 Live Demo

**Frontend:** https://vendorguard-web.web.app/

**Repository:** https://github.com/agrima150103/vendorguard-ai

VendorGuard is an evidence-first vendor-risk decision-support system designed to identify:

- unsupported vendor claims
- contradictory evidence
- missing security controls
- manipulated or adversarial content
- prompt-injection attempts
- policy violations requiring human review

The system allows agents to analyze and recommend outcomes, but **only a human reviewer can record the final high-risk decision**.

---

## 🎯 Problem

Vendor onboarding often requires analysts to review security questionnaires, policy evidence, compliance claims, and risk indicators manually.

An autonomous AI system introduces another problem: a malicious or contradictory document could influence the model into making an unsafe vendor decision.

VendorGuard addresses both concerns by combining:

**multi-agent analysis + evidence traceability + deterministic policy checks + prompt-injection defense + human approval**

rather than allowing an LLM to make unrestricted final decisions.

---

## ✨ What Makes VendorGuard Different

### 🤖 Four Specialized Agents

VendorGuard separates responsibilities across four Google ADK agents:

1. **Evidence Agent**
   - extracts vendor claims
   - tracks evidence provenance
   - identifies missing or unsupported information

2. **Risk & Security Agent**
   - evaluates security controls
   - identifies contradictions
   - assigns structured risk findings

3. **Policy Agent**
   - queries governed policy rules through MCP
   - checks whether proposed actions are permitted
   - prevents policy decisions from relying only on model judgment

4. **Decision & Report Agent**
   - consolidates evidence and risk findings
   - generates a recommendation
   - produces a structured assessment report

The agents can recommend an outcome, but the final decision remains subject to a **human approval gate**.

---

## 🏗️ Architecture

```text
                         ┌──────────────────┐
                         │     React UI     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    FastAPI API   │
                         └────────┬─────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    Assessment Workflow    │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
 ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
 │ Evidence Agent  │    │ Risk & Security │    │   Policy Agent  │
 │                 │    │      Agent      │    │   + MCP Tools   │
 └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  ▼
                       ┌────────────────────┐
                       │ Decision & Report  │
                       │       Agent        │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │ Human Approval Gate│
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │ Structured Audit   │
                       │      Trail         │
                       └────────────────────┘