#!/usr/bin/env python3
"""One-time Garmin auth setup — handles MFA and saves session token."""
from __future__ import annotations

import json
import os
from pathlib import Path

ENV_FILE = Path.home() / ".claude" / "garmin" / ".env"
TOKEN_DIR = Path.home() / ".claude" / "garmin" / "tokens"


def load_env() -> None:
    if not ENV_FILE.exists():
        print(f"ERROR: {ENV_FILE} not found.")
        print("Copy ~/.claude/garmin/.env.example → ~/.claude/garmin/.env and fill in your credentials.")
        raise SystemExit(1)
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def prompt_mfa() -> str:
    return input("Enter MFA/2FA code from your authenticator app: ").strip()


def main() -> None:
    load_env()

    email = os.environ.get("GARMIN_EMAIL", "")
    password = os.environ.get("GARMIN_PASSWORD", "")
    if not email or not password:
        print("ERROR: GARMIN_EMAIL and GARMIN_PASSWORD must be set in ~/.claude/garmin/.env")
        raise SystemExit(1)

    try:
        from garminconnect import Garmin  # type: ignore[import]
    except ImportError:
        print("ERROR: garminconnect not installed.")
        print("Run: uv tool install garminconnect")
        raise SystemExit(1)

    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Logging in as {email}...")

    client = Garmin(email=email, password=password, prompt_mfa=prompt_mfa)

    try:
        client.login()
    except Exception as e:
        print(f"Login failed: {e}")
        raise SystemExit(1)

    client.garth.dump(str(TOKEN_DIR))
    print(f"\nSuccess! Session token saved to {TOKEN_DIR}")
    print("You can now use /garmin in Claude Code.")

    # Quick sanity check
    try:
        name = client.get_full_name()
        print(f"Logged in as: {name}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
