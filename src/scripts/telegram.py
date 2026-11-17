# ---------------------------------------------------------
# Copyright (C) 2026 krvstek (Original Author)
# Copyright (C) 2026 The uni-apks Contributors (Modifications)
# 
# DO NOT REMOVE OR ALTER THIS COPYRIGHT HEADER.
# This file is part of uni-apks.
# Canonical source: https://github.com/krvstek/uni-apks
#
# Licensed under the GNU GPLv3. You may modify this file,
# but you MUST keep this original copyright notice intact
# and prominently state any changes made.
# See the AUTHORS file in the root directory for details.
# ---------------------------------------------------------

import argparse
import os
import re
from pathlib import Path

from curl_cffi import requests as curl_requests

from src.core.logger import IS_GITHUB, abort, epr, pr

_BACKTICK_RE = re.compile(r"`([^`]+)`")
# A download-table row: "| Music | `9.30.53` | `arm64-v8a` | [**⬇️ APK**](url) |"
_ROW_RE = re.compile(r"^\| (?P<name>[^|]+?) \| (?P<ver>`[^`]+`) \| (?P<arch>[^|]+?) \| (?:\[[^\]]*\]\((?P<url>[^)]+)\)|—) \|$")


def _require_ci(script: str) -> None:
    if not IS_GITHUB:
        abort(f"'{script}' is only available in GitHub Actions")

def _parse_final_md(final_md: Path) -> tuple[list[str], str, list[str]]:
    """Read the release notes written by src.scripts.logs back into Telegram lines."""
    green_lines: list[str] = []
    microg_line: str = ""
    changelog_lines: list[str] = []
    for line in final_md.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and (m := _ROW_RE.match(stripped)):
            name, version, arch = m["name"].strip(), _BACKTICK_RE.sub(r"\1", m["ver"]), _BACKTICK_RE.sub(r"\1", m["arch"]).strip()
            label = f"{name} ({arch})" if arch != "Universal" else name
            green_lines.append(f"🟢 » {label}: [{version}]({m['url']})" if m["url"] else f"🟢 » {label}: {version}")
        elif stripped.startswith("| Patches |") and (link := re.search(r"\[`([^`]+)`]\(([^)]+)\)", stripped)):
            changelog_lines.append(f"[🔗 » Changelog ({link.group(1)})]({link.group(2)})")
        elif not microg_line and "[MicroG-RE](" in stripped and (link := re.search(r"\[MicroG-RE]\(([^)]+)\)", stripped)):
            microg_line = f"▶️ » Install [MicroG-RE]({link.group(1)}) to enable Google account sign-in for supported apps"
    return green_lines, microg_line, changelog_lines

def _build_message(brand: str, green_lines: list[str], microg_line: str, changelog_lines: list[str]) -> str:
    title = os.getenv("RELEASE_TITLE") or brand.capitalize()
    parts: list[str] = [f"*New build: {title}*", ""]
    parts.extend(green_lines)
    if microg_line:
        parts.extend(["", microg_line])
    if changelog_lines:
        parts.append("")
        parts.extend(changelog_lines)
    return "\n".join(parts)

def notify(brand: str, final_md_path: Path | str = "final.md") -> None:
    token = os.getenv("TG_TOKEN")
    chat = os.getenv("TG_CHAT")
    if not token or not chat:
        epr("TG_TOKEN or TG_CHAT not set, skipping notification")
        return

    path = Path(final_md_path)
    if not path.is_file() or path.stat().st_size == 0:
        epr(f"'{final_md_path}' not found or empty, skipping notification")
        return

    green_lines, microg_line, changelog_lines = _parse_final_md(path)
    if not green_lines:
        epr("No build results found in final.md, skipping notification")
        return

    msg = _build_message(brand, green_lines, microg_line, changelog_lines)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat, "text": msg, "parse_mode": "Markdown", "link_preview_options": {"is_disabled": True}}
    pr(f"Sending Telegram notification for '{brand}' to '{chat}'")
    with curl_requests.Session() as session:
        resp = session.post(url, json=payload, timeout=(5, 10))
        if resp.status_code != 200:
            epr(f"Telegram API error {resp.status_code}: {resp.text}")
        else:
            pr("Telegram notification sent successfully")

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m src.scripts.telegram",
        description="Send a build summary notification to Telegram.",
    )
    parser.add_argument(
        "--brand",
        required=True,
        help="Brand / patch source name for the notification header",
    )
    parser.add_argument(
        "--final-md",
        default="final.md",
        help="Path to the combined markdown release notes file (default: final.md)",
    )
    args = parser.parse_args(argv)
    if not args.brand.strip():
        parser.error("--brand cannot be empty")
    if not args.final_md.strip():
        parser.error("--final-md cannot be empty")
    return args

def main() -> None:
    args = _parse_args()
    _require_ci("telegram.py")
    notify(args.brand, args.final_md)

if __name__ == "__main__":
    main()
