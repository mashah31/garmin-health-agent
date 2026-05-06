#!/usr/bin/env python3
"""Fetch comprehensive Garmin health data and output as JSON."""
from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path


TOKEN_DIR = Path.home() / ".claude" / "garmin" / "tokens"
ENV_FILE = Path.home() / ".claude" / "garmin" / ".env"


def load_env() -> None:
    if not ENV_FILE.exists():
        bail(f"No credentials found. Copy ~/.claude/garmin/.env.example to ~/.claude/garmin/.env and fill in your details.")
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def bail(msg: str) -> None:
    print(json.dumps({"error": msg}))
    sys.exit(1)


def safe(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        return {"_unavailable": str(e)}


def main() -> None:
    load_env()

    email = os.environ.get("GARMIN_EMAIL", "")
    password = os.environ.get("GARMIN_PASSWORD", "")
    if not email or not password:
        bail("GARMIN_EMAIL and GARMIN_PASSWORD must be set in ~/.claude/garmin/.env")

    try:
        from garminconnect import Garmin  # type: ignore[import]
    except ImportError:
        bail("garminconnect not available. Run the skill via: uv run --with garminconnect python ~/.claude/garmin/fetch_health.py")

    client = Garmin(email=email, password=password)
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)

    # Try stored token first, fall back to password login
    try:
        client.login(tokenstore=str(TOKEN_DIR))
    except Exception:
        try:
            client.login()
            client.garth.dump(str(TOKEN_DIR))
        except Exception as e:
            if "MFA" in str(e) or "2FA" in str(e) or "NEEDS_MFA" in str(e):
                bail("MFA required for first login. Run: uv run --with garminconnect python ~/.claude/garmin/setup.py")
            bail(f"Authentication failed: {e}. Run setup: uv run --with garminconnect python ~/.claude/garmin/setup.py")

    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    month_ago = (date.today() - timedelta(days=30)).isoformat()

    data: dict = {
        "fetched_at": today,

        # --- Core daily health ---
        "daily_stats": safe(client.get_stats, today),
        "user_summary": safe(client.get_user_summary, today),

        # --- Sleep (last night = yesterday) ---
        "sleep": safe(client.get_sleep_data, yesterday),

        # --- Heart & cardiovascular ---
        "hrv": safe(client.get_hrv_data, today),
        "resting_hr": safe(client.get_rhr_day, today),
        "heart_rates_today": safe(client.get_heart_rates, today),
        "respiration": safe(client.get_respiration_data, today),
        "spo2": safe(client.get_spo2_data, today),

        # --- Recovery & readiness ---
        "body_battery_week": safe(client.get_body_battery, week_ago, today),
        "training_readiness": safe(client.get_training_readiness, today),
        "morning_readiness": safe(client.get_morning_training_readiness, today),
        "training_status": safe(client.get_training_status, today),

        # --- Stress ---
        "stress_today": safe(client.get_stress_data, today),
        "stress_weekly": safe(client.get_weekly_stress, today, 4),  # last 4 weeks

        # --- Movement ---
        "steps_today": safe(client.get_steps_data, today),
        "steps_week": safe(client.get_daily_steps, week_ago, today),
        "intensity_minutes": safe(client.get_intensity_minutes_data, today),
        "floors": safe(client.get_floors, today),

        # --- Activities ---
        "last_activity": safe(client.get_last_activity),
        "activities_week": safe(client.get_activities_by_date, week_ago, today),

        # --- Performance & fitness ---
        "max_metrics": safe(client.get_max_metrics, today),           # VO2 max, fitness age
        "endurance_score": safe(client.get_endurance_score, month_ago, today),
        "race_predictions": safe(client.get_race_predictions),
        "personal_records": safe(client.get_personal_record),
        "hill_score": safe(client.get_hill_score, month_ago, today),
        "running_tolerance": safe(client.get_running_tolerance, month_ago, today),
        "lactate_threshold": safe(client.get_lactate_threshold),

        # --- Body ---
        "body_composition": safe(client.get_body_composition, month_ago, today),
        "weight": safe(client.get_weigh_ins, month_ago, today),
    }

    print(json.dumps(data, default=str, indent=2))


if __name__ == "__main__":
    main()
