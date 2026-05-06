# garmin-health-agent

A personal AI health doctor powered by Claude Code and your Garmin data.

Type `/garmin` in Claude Code and get a comprehensive health assessment — sleep quality, recovery status, cardiovascular health, stress, training readiness, VO2 max trends, race predictions, and a specific recommendation for your day.

---

## What it does

Fetches data from Garmin Connect across 30+ health metrics and passes it to Claude, which responds as your personal health doctor. It covers:

| Category | Metrics |
|---|---|
| Sleep | Duration, stages (deep/REM/light), HRV, SpO2, sleep score |
| Recovery | Body battery, training readiness, morning readiness |
| Cardiovascular | Resting HR, HRV baseline, respiration rate, SpO2 |
| Stress | Daily stress timeline, weekly stress balance |
| Activity | Steps, intensity minutes, floors, weekly activity load |
| Performance | VO2 max, fitness age, endurance score, lactate threshold |
| Racing | Race predictions (5K / 10K / HM / Marathon), personal records |
| Body | Weight, body composition trends |

Claude analyzes everything together — not just today's numbers but trends over the past week and month — and gives you a verdict: should you train hard, go easy, or rest? Why? What's the one thing to fix?

---

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- [uv](https://docs.astral.sh/uv/) package manager
- A Garmin device + Garmin Connect account

---

## Setup

**1. Install the garminconnect library:**
```bash
uv tool install garminconnect
```

**2. Add your credentials:**
```bash
cp .env.example .env
# Edit .env — add your Garmin Connect email and password
```

**3. Copy the skill into Claude Code's global commands:**
```bash
mkdir -p ~/.claude/commands ~/.claude/garmin
cp garmin.md ~/.claude/commands/garmin.md
cp scripts/fetch_health.py ~/.claude/garmin/fetch_health.py
cp scripts/setup.py ~/.claude/garmin/setup.py
cp .env.example ~/.claude/garmin/.env.example
# Then copy your filled-in .env too:
cp .env ~/.claude/garmin/.env
```

**4. Run first-time auth** (handles MFA if your account uses it):
```bash
uv run --with garminconnect python ~/.claude/garmin/setup.py
```

This saves a session token to `~/.claude/garmin/tokens/`. You won't need to re-authenticate for weeks.

---

## Usage

Open Claude Code and type:

```
/garmin
```

That's it. Claude fetches your data and returns a full health report in about 10–15 seconds.

---

## How it works

```
/garmin
   ↓
garmin.md (skill) instructs Claude to run fetch_health.py
   ↓
fetch_health.py authenticates with Garmin Connect (using stored token)
   ↓
Fetches ~30 health metrics for today + last 7–30 days
   ↓
Outputs structured JSON
   ↓
Claude analyzes as personal health doctor
   ↓
Comprehensive health report with today's recommendation
```

The skill prompt instructs Claude to flag trends across multiple days — not just snapshot values — which is what makes it genuinely useful. A single bad sleep night is noise; a week of declining HRV is a signal.

---

## Credentials & Security

- Your credentials live only in `~/.claude/garmin/.env` — never committed (`.gitignore` covers it)
- After first login, only a session token is used — your password is not sent again
- Garmin Connect does not have an official public API; this uses the same endpoints as the Garmin Connect mobile app via the [garminconnect](https://github.com/cyberjunky/python-garminconnect) library

---

## Project structure

```
garmin-health-agent/
  garmin.md          ← Claude Code skill (the /garmin slash command)
  scripts/
    fetch_health.py  ← fetches all Garmin data, outputs JSON
    setup.py         ← one-time interactive auth setup (handles MFA)
  .env.example       ← credential template
  .gitignore
  README.md
```

---

## Author

**Manan Shah** — [github.com/mashah31](https://github.com/mashah31)

---

## License

MIT
