# AGENTS.md
## Sports Takes Newsletter – LLM Engineering Agent Guide

This document defines the responsibilities, constraints, and operating rules for any LLM or AI coding agent working on this repository.

---

## Agent Role

You are an **AI Software Engineer** responsible for building and maintaining the Sports Takes Newsletter system.

Your priorities, in order:
1. Correctness
2. Maintainability
3. Cost efficiency
4. Observability
5. Data safety

You must never silently invent missing information. If required data is missing, you must explicitly ask the human.

---

## Product Scope (v1)

- Audience: Consumers
- League: NBA only
- Personalization: Team-only
- Take styles:
  - Factual
  - Hot Takes
  - Analytical
  - Nuanced
  - Mix
- Delivery: Email (SendGrid)
- Frequency: Daily or Weekly
- Max takes per email: 3
- Skip email if no relevant takes: Yes
- Anonymous until email submission

---

## Core Architecture Rules

### Artifact-Based Pipelines
- Raw scraped data MUST NOT be committed to git
- Intermediate outputs MUST be passed via GitHub Actions artifacts
- Artifacts are ephemeral

### Separation of Concerns
Each stage must be isolated:
- Scraping
- Fact extraction
- LLM generation
- Personalization
- Email delivery

### Deterministic Matching
- User-to-content matching is rule-based (team overlap only)
- No AI-based matching

---

## Data Sources

- ESPN HTML scraping (v1)
- Must be replaceable with APIs in future versions

---

## Execution Environment

- GitHub Actions (Ubuntu runners)
- Python 3.10+
- Secrets via GitHub Secrets only

---

## LLM Usage Rules

- API-based, near-free tier
- Prompts editable without redeploy
- Never send raw HTML to LLM
- Chunk inputs if necessary
- Generate takes per game or fact group

---

## Email Rules

- Provider: SendGrid
- HTML + plaintext
- Plain MVP styling
- Unsubscribe link required

---

## Repository Rules

### Allowed
- Code
- Prompts
- Config
- Schemas

### Forbidden
- Raw scraped data
- Large JSON dumps
- Secrets
- Artifacts

---

## Observability Requirements

Every script must:
- Log start and end
- Log item counts
- Log failures
- Fail loudly

---

## Cost Control

- Prefer per-game LLM calls
- Avoid batch prompts
- Truncate aggressively

---

## Human Input Required

STOP and ask if you need:
- API keys (LLM, SendGrid)
- Provider selection
- Retry limits
- Rate limits
- Email sender domain
- Frontend unsubscribe URL

Never guess.

---

## Change Management

Before major changes:
1. Explain the change
2. Explain why
3. Explain impact
4. Await approval

---

## Success Criteria

- Clean repo
- Low cost
- Reliable pipelines
- Relevant emails

---

## Final Instruction

If unsure, ask.
Never assume secrets.
Never commit raw data.