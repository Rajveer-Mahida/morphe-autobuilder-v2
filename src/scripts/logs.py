# ---------------------------------------------------------
# Copyright (C) 2026 krvstek
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
# Modified in the morphe-autobuilder-v2 fork: the per-app build logs are now
# rendered as structured release notes (download table, build details, install
# steps, signing certificate) instead of being concatenated line by line.

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

from src.core.logger import IS_GITHUB, abort

# "- 🟢 » Music Experimental (arm64-v8a): [`9.46.51`](https://…/music-….apk)"
_BUILD_RE = re.compile(r"^- 🟢 » (?P<name>.+?)(?: \((?P<details>[^)]*)\))?: (?:\[`(?P<ver>[^`]+)`\]\((?P<url>[^)]+)\)|`(?P<ver_plain>[^`]+)`)$")
_COMPONENT_RE = re.compile(r"^> ⚙️ » (?P<kind>CLI|Patches): `(?P<file>[^`]+)`")
_LINK_RE = re.compile(r"\[[^\]]*\]\((?P<url>[^)]+)\)")
_SIGNER_RE = re.compile(r"^> 🔐 » Signer: `(?P<cert>[^`]+)`")
_MICROG_FALLBACK = "https://github.com/MorpheApp/MicroG-RE/releases"
_ARCH_ORDER = {"arm64-v8a": 0, "armeabi-v7a": 1, "x86_64": 2, "x86": 3}


def _require_ci(script: str) -> None:
    if not IS_GITHUB:
        abort(f"'{script}' is only available in GitHub Actions")

@dataclass(slots=True, frozen=True)
class _Build:
    name: str
    arch: str
    version: str
    url: str

@dataclass(slots=True)
class _Notes:
    builds: list[_Build] = field(default_factory=list)
    patches: dict[str, str] = field(default_factory=dict)  # file -> changelog url
    cli: list[str] = field(default_factory=list)
    signers: list[str] = field(default_factory=list)
    microg_url: str = ""

def _parse_log_file(log: Path, notes: _Notes) -> None:
    lines = [s for ln in log.read_text(encoding="utf-8").splitlines() if (s := ln.strip())]
    for i, line in enumerate(lines):
        if m := _BUILD_RE.match(line):
            details = [d.strip() for d in (m["details"] or "").split(",") if d.strip()]
            arch = next((d for d in details if d in _ARCH_ORDER), "")
            notes.builds.append(_Build(m["name"], arch, m["ver"] or m["ver_plain"], m["url"] or ""))
        elif m := _SIGNER_RE.match(line):
            if m["cert"] not in notes.signers:
                notes.signers.append(m["cert"])
        elif line.startswith("▶️") and "MicroG" in line:
            if link := _LINK_RE.search(line):
                notes.microg_url = notes.microg_url or link["url"]
        elif m := _COMPONENT_RE.match(line):
            if m["kind"] == "CLI":
                if m["file"] not in notes.cli:
                    notes.cli.append(m["file"])
            else:
                nxt = lines[i + 1] if i + 1 < len(lines) else ""
                link = _LINK_RE.search(nxt) if "Changelog" in nxt else None
                notes.patches.setdefault(m["file"], link["url"] if link else "")

def _render(notes: _Notes) -> str:
    out: list[str] = []

    if notes.patches:
        sources = []
        for file, url in notes.patches.items():
            # ".../MorpheApp/morphe-patches/releases/tag/v2.3.0" names the repo and version better than the file
            m = re.search(r"(?:github|gitlab)\.com/([^/]+/[^/]+)/(?:-/)?releases/(?:tag/)?([^/?#]+)", url)
            label = f"**{m.group(1)} {m.group(2)}**" if m else f"**{file}**"
            sources.append(f"[{label}]({url})" if url else label)
        out += [f"Pre-patched apps built with {', '.join(sources)}. Every APK below is signed with the same key, so future releases install as updates.", ""]

    out += ["### 📱 Downloads", "", "| App | Version | Architecture | Download |", "| :--- | :---: | :---: | :---: |"]
    builds = sorted(dict.fromkeys(notes.builds), key=lambda b: (b.name.lower(), _ARCH_ORDER.get(b.arch, 9)))
    for b in builds:
        arch = f"`{b.arch}`" if b.arch else "Universal"
        dl = f"[**APK**]({b.url})" if b.url else "—"
        out.append(f"| {b.name} | `{b.version}` | {arch} | {dl} |")

    out += ["", "### 🧩 Build details", "", "| Component | Version |", "| :--- | :--- |"]
    for file, url in notes.patches.items():
        out.append(f"| Patches | [`{file}`]({url}) |" if url else f"| Patches | `{file}` |")
    for file in notes.cli:
        out.append(f"| Patcher CLI | `{file}` |")
    for cert in notes.signers:
        out.append(f"| Signing certificate (SHA-256) | `{cert}` |")

    microg = notes.microg_url or _MICROG_FALLBACK
    out += [
        "",
        "### 📲 Installation",
        "",
        "1. **Choose your architecture.** Most phones from the last few years are `arm64-v8a`; older or budget devices may need `armeabi-v7a`. *Universal* builds run on both.",
        "2. **Remove conflicting installs.** Uninstall any copy of the same app that was signed by someone else - Android will not update across signing keys.",
        f"3. **Google sign-in.** YouTube and YouTube Music need [MicroG-RE]({microg}) installed for account login.",
    ]
    if notes.signers:
        out += [
            "",
            "> [!TIP]",
            "> To verify a download, run `apksigner verify --print-certs <file>.apk` and compare its certificate SHA-256 with the one above.",
        ]
    return "\n".join(out) + "\n"

def combine_logs(logs_dir: Path | str = "logs") -> None:
    logs = sorted(Path(logs_dir).rglob("build*.md"))
    if not logs:
        return

    notes = _Notes()
    for log in logs:
        _parse_log_file(log, notes)
    if notes.builds:
        print(_render(notes), end="")

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m src.scripts.logs",
        description="Combine per-app markdown build logs into release notes.",
    )
    parser.add_argument(
        "--logs-dir",
        default="logs",
        help="Directory containing build*.md log files (default: logs)",
    )
    args = parser.parse_args(argv)
    if not args.logs_dir.strip():
        parser.error("--logs-dir cannot be empty")
    return args

def main() -> None:
    args = _parse_args()
    _require_ci("logs.py")
    combine_logs(args.logs_dir)

if __name__ == "__main__":
    main()
