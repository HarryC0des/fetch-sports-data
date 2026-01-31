# Sports Takes Newsletter (NBA)

Sports Takes Newsletter delivers personalized NBA takes via email. The system
scrapes ESPN recaps, extracts structured facts, generates LLM takes, matches
them to user team preferences, and sends emails through SendGrid. GitHub Actions
orchestrates the pipeline using artifacts (no scraped data committed).

## Web Signup

Run the signup web app locally:
```bash
pip install -r requirements.txt
python web/app.py
```

### Routes
- `GET /` → Signup page
- `POST /api/signup` → Persist user preferences to Supabase

### Required environment variables
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key
```

### Signup fields
- Name (required)
- Email (required, validated)
- NBA Teams (multi-select, max 5)
- Take style (Factual, Hot Takes, Analytical, Nuanced, Mix)
- Email frequency (daily or weekly)

## GitHub Actions Pipelines

- `ingest.yml` → Fetch game IDs + ESPN recaps (artifacts)
- `generate.yml` → Extract facts + generate takes (artifacts)
- `send_emails.yml` → Personalize + send emails

Required GitHub Secrets:
- `OPEN_ROUTER_KEY`
- `SENDGRID_API_KEY`
- `SENDGRID_FROM_EMAIL`
- `SENDGRID_ASM_GROUP_ID`
- `SUPABASE_KEY`

## Documentation

- Product/engineering docs: `docs/AI_docs/`
- Render deployment: `docs/RENDER_ENV.md`
