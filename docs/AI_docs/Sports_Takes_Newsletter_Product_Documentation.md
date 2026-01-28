# 🏀 Sports Takes Newsletter  
**Product & Technical Documentation (v1)**

---

## 1. Product Overview

### Summary
Sports Takes Newsletter is a consumer-facing product that delivers **personalized, AI-generated sports takes** via email. Users select their favorite NBA teams and preferred take style, then receive curated insights on a daily or weekly cadence.

The system automatically:
1. Scrapes ESPN for NBA game recaps
2. Extracts relevant sports facts
3. Uses an LLM to generate opinionated sports takes
4. Matches takes to user interests
5. Sends personalized emails

This product emphasizes **automation, personalization, and low operational cost** in v1, with a roadmap toward richer data sources, styling, and paid LLM usage.

---

## 2. Goals & Non-Goals

### Goals (v1)
- Deliver high-quality NBA sports takes via email
- Allow users to personalize by **team** and **take style**
- Operate at near-zero cost using free LLM APIs
- Maintain a clean, scalable pipeline architecture
- Avoid committing scraped data to the repository

### Non-Goals (v1)
- Real-time alerts or live updates
- Player-level personalization
- In-app content consumption
- Paid subscriptions or monetization
- Multi-league support (NBA only)

---

## 3. Target Users
- Consumers / sports fans
- Casual to moderately engaged NBA followers
- Users who want insight without reading full recaps

---

## 4. User Experience & Flow

1. User visits landing page
2. Selects favorite NBA team(s)
3. Chooses take style: Factual, Hot Takes, Analytical, Nuanced, Mix
4. Chooses frequency (Daily / Weekly)
5. Submits email address
6. Receives personalized emails
7. Can unsubscribe via email footer link

---

## 5. Take Styles

| Style | Description |
|------|-------------|
| Factual | Straightforward analysis |
| Hot Takes | Bold, opinionated |
| Analytical | Data-driven |
| Nuanced | Balanced perspectives |
| Mix | Combination of styles |

---

## 6. System Architecture

```
[ Web App ]
     ↓
[ User Database ]
     ↓
[ Daily Ingestion Pipeline ]
     ↓
[ Fact Extraction ]
     ↓
[ LLM Take Generation ]
     ↓
[ Personalization ]
     ↓
[ Email Delivery ]
```

---

## 7. Data Ingestion

- Source: ESPN (NBA only)
- Method: HTML scraping
- Frequency: Once per day
- Storage: GitHub Actions artifacts (no repo commits)

---

## 8. Fact Identification

- Rule-based extraction
- Team-name matching
- One fact group per game

Example:
```json
{
  "teams": ["Lakers"],
  "fact": "LeBron scored 38 points in a win."
}
```

---

## 9. LLM Integration

- API-based (free tier)
- Prompt templates stored outside code
- Style applied at prompt time

---

## 10. Personalization

- Team-only matching
- Max 3 takes per email
- Skip email if no relevant takes

---

## 11. Email Delivery

- Provider: SendGrid
- Format: HTML + Plain text
- Plain MVP design
- Unsubscribe via SendGrid ASM footer link (per-user)

---

## 12. Orchestration

- GitHub Actions
- Separate workflows for ingestion and delivery
- Artifacts used to pass data between steps

---

## 13. Data Storage

- PostgreSQL (recommended)
- Tables:
  - Users
  - Interests
  - Takes
  - Delivery state

---

## 14. Secrets & Config

- GitHub Secrets
- API keys for LLM + SendGrid

---

## 15. Observability

- Logs in workflows
- Metrics:
  - Emails sent
  - Takes generated
  - Failures
- Alerts on failure

---

## 16. Security & Ethics

- Email-only PII
- No scraping behind auth
- Plan to migrate to official APIs

---

## 17. Roadmap

- Multi-league support
- Player-level interests
- Designed newsletters
- Paid LLM models
- Preference center

---

## 18. Success Metrics

- Open rate
- CTR
- Retention
- Unsubscribe rate
- Cost per send

---

## 19. Summary

A scalable, low-cost, AI-powered sports newsletter built with clean data pipelines, strong personalization, and room to grow.
