## Render Environment Configuration (.env)

This project reads configuration from environment variables (no secrets are stored in code).
On Render, set these values in the **Environment** section for your web service.

### Required for the signup web app
- `SUPABASE_URL` — Supabase project URL
- `SUPABASE_KEY` — Supabase service role key (server-side only)

### Optional (Render sets this automatically)
- `PORT` — Render injects the port used by gunicorn

### Local development example
Create a `.env` file locally (do **not** commit it):
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key
```

Then export the variables before running the app:
```bash
set -a
source .env
set +a
python web/app.py
```

### Render start command
Use gunicorn in production:
```bash
gunicorn -w 2 -b 0.0.0.0:$PORT web.app:app
```

### Notes
- Keep secrets in Render environment settings or GitHub Secrets.
- Never commit `.env` files to the repository.
