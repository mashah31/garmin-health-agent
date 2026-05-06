# garmin-health-agent

A personal AI health doctor, delivered as a **Claude Code skill**.

Type `/garmin` anywhere in Claude Code and get a full health assessment based on your Garmin data — sleep, recovery, HRV, stress, training readiness, VO2 max, race predictions, and a specific recommendation for your day.

---

## What is a Claude Code Skill?

A skill is a slash command you can invoke inside Claude Code (e.g. `/garmin`). It's a Markdown file that gives Claude a set of instructions to follow when triggered — including running shell commands, fetching data, and formatting a response.

Skills live in `~/.claude/commands/`. Any `.md` file you drop there becomes a `/command` you can call from anywhere.

```
~/.claude/commands/
  garmin.md     ← typing /garmin loads and executes this file
  review.md     ← typing /review would load this one
  ...
```

This repo contains one skill: `/garmin`.

---

## How it works

When you type `/garmin`, this is what happens under the hood:

```
You type: /garmin
    │
    ▼
Claude Code reads ~/.claude/commands/garmin.md
    │
    ▼
The skill instructs Claude to run:
  uv run --with garminconnect python ~/.claude/garmin/fetch_health.py
    │
    ▼
fetch_health.py authenticates with Garmin Connect (using a cached token)
and fetches ~30 health metrics for today + last 7–30 days → outputs JSON
    │
    ▼
Claude receives the JSON and analyzes it as your personal health doctor
    │
    ▼
Full health report with today's recommendation
```

The two folders involved:

| Folder | Purpose |
|---|---|
| `~/.claude/commands/garmin.md` | The skill itself — Claude reads this when you type `/garmin` |
| `~/.claude/garmin/` | Scripts + credentials — what the skill calls at runtime |

This repo is the **source of truth**. `install.sh` syncs it into `~/.claude/` where Claude Code can find it.

---

## What it reports

| Category | Metrics |
|---|---|
| Sleep | Duration, stages (deep/REM/light), HRV, SpO2, sleep score |
| Recovery | Body battery, training readiness, morning readiness |
| Cardiovascular | Resting HR, HRV baseline, respiration rate, SpO2 |
| Stress | Daily stress timeline, 4-week stress trend |
| Activity | Steps, intensity minutes, floors, weekly activity load |
| Performance | VO2 max, fitness age, endurance score, lactate threshold |
| Racing | Race predictions (5K / 10K / HM / Marathon), personal records |
| Body | Weight, body composition trends |

Claude analyzes trends across the week and month — not just today's snapshot — which is what makes the output genuinely useful rather than generic.

---

## Requirements

- [Claude Code](https://claude.ai/code) CLI
- [uv](https://docs.astral.sh/uv/) — Python package manager
- A Garmin device + Garmin Connect account

---

## Setup

**1. Clone the repo:**
```bash
git clone https://github.com/mashah31/garmin-health-agent.git
cd garmin-health-agent
```

**2. Run the installer:**
```bash
./install.sh
```

This copies `garmin.md` into `~/.claude/commands/` and the scripts into `~/.claude/garmin/`. It also creates `~/.claude/garmin/.env` from the template if one doesn't exist yet.

**3. Add your credentials:**
```bash
# Edit the file that install.sh just created
nano ~/.claude/garmin/.env
```
Fill in your Garmin Connect email and password.

**4. Authenticate (one time only):**
```bash
uv run --with garminconnect python ~/.claude/garmin/setup.py
```

This logs in, handles MFA if your account uses it, and saves a session token to `~/.claude/garmin/tokens/`. You won't need to re-authenticate for weeks.

**5. Use it:**
```
/garmin
```

---

## Updating the skill

If you pull new changes from this repo and want to apply them:

```bash
git pull
./install.sh
```

`install.sh` always overwrites the skill and scripts in `~/.claude/`. Your `.env` and tokens are never touched.

---

## File structure

```
garmin-health-agent/
  install.sh           ← syncs this repo → ~/.claude/ (run this after cloning or pulling)
  garmin.md            ← the Claude Code skill (/garmin slash command definition)
  scripts/
    fetch_health.py    ← fetches all Garmin metrics, outputs JSON
    setup.py           ← one-time interactive auth (handles MFA)
  .env.example         ← credential template (copy → ~/.claude/garmin/.env)
  .gitignore           ← keeps .env and tokens out of git
  README.md
```

---

## Credentials & security

- Credentials live only in `~/.claude/garmin/.env` — never in this repo (`.gitignore` enforces it)
- After first login, only a session token is used — your password isn't sent again
- `uv run --with garminconnect` downloads the library into a local cache on first run, then reuses it — nothing is installed globally

Garmin Connect has no official public API. This uses the same endpoints as the Garmin Connect mobile app via the [garminconnect](https://github.com/cyberjunky/python-garminconnect) library.

---

## Author

**Manan Shah** — [github.com/mashah31](https://github.com/mashah31)

---

## License

MIT
