# Stellar Chart — astrology subscription web app

Users create an account, pay a subscription in **USDT**, enter their birth date, time and place,
and get an accurate natal chart (Swiss Ephemeris), a personal daily horoscope by email or Telegram,
and AI answers to their questions based on their own chart.

## What's included

| Part | Where | Notes |
|---|---|---|
| Accounts (email + password, JWT) | `app/auth.py`, `app/routers/auth.py` | bcrypt hashing, account deletion (GDPR) |
| Birthplace → coordinates → historical time zone | `app/astrology/geo.py` | OpenStreetMap Nominatim + `timezonefinder` + IANA tz data (handles past DST rules) |
| Natal chart | `app/astrology/chart.py` | Planets, Placidus houses (Whole Sign fallback near poles), Ascendant/MC, aspects, elements; noon chart when birth time is unknown |
| Daily transits | `app/astrology/transits.py` | Today's sky vs. the natal chart |
| USDT payments | `app/services/payments.py`, `app/routers/payments.py` | NOWPayments invoices + signed IPN webhook; credits each payment once |
| AI readings & Q&A | `app/services/ai.py`, `app/routers/readings.py` | Claude API, grounded in the calculated chart; daily question limit |
| Daily notifications | `app/scheduler.py`, `app/services/notify.py` | Sent at each user's chosen local hour via Telegram and/or email |
| Telegram bot linking | `app/routers/telegram.py` | Users tap a personal `t.me/<bot>?start=…` link |
| Web frontend | `frontend/` | Sign-up, birth form, SVG chart wheel, placements, today's reading, Q&A, settings |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then fill in your keys
uvicorn app.main:app --reload
```

Open http://localhost:8000. API docs are at http://localhost:8000/docs. Run tests with `pytest`.

For PostgreSQL: `docker compose up -d` and set `DATABASE_URL=postgresql+psycopg2://astro:astro@localhost:5432/astro`.

## Keys you need

1. **NOWPayments** (nowpayments.io): create an account, add your USDT payout wallet, then copy the
   **API key** and **IPN secret** into `.env`. `PAY_CURRENCY=usdttrc20` (Tron) has the lowest fees.
   Your server must be reachable at `BASE_URL` over HTTPS for the payment webhook to arrive.
2. **Claude API** (console.anthropic.com): `ANTHROPIC_API_KEY`.
3. **Telegram** (optional): create a bot with @BotFather, set `TELEGRAM_BOT_TOKEN` and
   `TELEGRAM_BOT_USERNAME`, then register the webhook once:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<BASE_URL>/api/telegram/webhook&secret_token=<TELEGRAM_WEBHOOK_SECRET>"
   ```
4. **Email** (optional): any SMTP provider (e.g. Postmark, Brevo, Amazon SES).

## Before going live

- **Swiss Ephemeris license**: it is AGPL or a paid professional license from Astrodienst.
  A closed-source paid service generally needs the professional license — check astro.com/swisseph.
- **Geocoding**: the free Nominatim service allows about 1 request/second. For real traffic use a
  paid geocoder (OpenCage, Google) or cache results.
- **Database migrations**: tables are auto-created on start; add Alembic before changing models in production.
- **Deploy** behind HTTPS (Railway, Render, Fly.io or a VPS with Caddy/Nginx). Run a single app
  instance, or move the scheduler to its own worker so readings aren't sent twice.
- **Legal**: privacy policy (birth data is personal data), terms of service, an "entertainment only"
  disclaimer, and check crypto payment and tax rules where your business is registered.
- **Renewals**: crypto has no automatic recurring billing; consider email/Telegram reminders a few
  days before `subscribed_until`.
