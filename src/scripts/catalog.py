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
# Added in the morphe-autobuilder-v2 fork: writes APPS.md, the catalog of every
# app in config.toml grouped by patch source, so the list never drifts from
# what is actually built.
#
#   python -m src.scripts.catalog --repo owner/name

import argparse
from pathlib import Path

from src.core.config import (
    CONFIG_PATH,
    AppEntry,
    load_toml,
    parse_app_entries,
    parse_config,
)

_ARCH_LABEL = {"all": "Universal", "both": "`arm64-v8a` · `armeabi-v7a`"}


def _source_link(spec: str) -> str:
    host, _, repo = spec.partition(":")
    return f"[{repo}](https://{'gitlab.com' if host == 'gitlab' else 'github.com'}/{repo})"

def _title(entries: list[AppEntry]) -> str:
    return next((e.brand_title for e in entries if e.brand_title), "") or entries[0].brand.replace("-", " ").title()

def render(repo: str) -> str:
    data = load_toml(CONFIG_PATH)
    entries = [e for e in parse_app_entries(data, parse_config(data)) if e.enabled]
    by_brand: dict[str, list[AppEntry]] = {}
    for e in entries:
        by_brand.setdefault(e.brand.lower(), []).append(e)

    order = sorted(by_brand, key=lambda b: (-len(by_brand[b]), b))
    out = [
        "# 📚 All apps",
        "",
        f"Every app this repository builds: **{len(entries)} apps** from **{len(by_brand)} patch sources**.",
        "Each patch source publishes its own releases, tagged `<source>-<patch version>`.",
        "",
        "> [!NOTE]",
        "> This file is generated from `config.toml` by `python -m src.scripts.catalog` - edit the config, not this file.",
        "",
        "| Patch source | Apps | Releases |",
        "| :--- | :---: | :---: |",
    ]
    for b in order:
        group = by_brand[b]
        anchor = b.replace(" ", "-")
        out.append(f"| [{_title(group)}](#{anchor}) | {len(group)} | [Releases](https://github.com/{repo}/releases?q={b}-&expanded=true) |")

    for b in order:
        group = sorted(by_brand[b], key=lambda e: e.app_name.lower())
        sources = list(dict.fromkeys(s for e in group for s in e.patches))
        out += [
            "",
            f'<a id="{b.replace(" ", "-")}"></a>',
            f"## {_title(group)}",
            "",
            f"Patches: {', '.join(_source_link(s) for s in sources)} · [Releases](https://github.com/{repo}/releases?q={b}-&expanded=true)",
            "",
            "| App | Architecture |",
            "| :--- | :---: |",
        ]
        out += [f"| {e.app_name} | {_ARCH_LABEL.get(e.arch, f'`{e.arch}`')} |" for e in group]
    return "\n".join(out) + "\n"

def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m src.scripts.catalog", description="Write APPS.md from config.toml.")
    parser.add_argument("--repo", required=True, help="GitHub repository the release links point at, as owner/name")
    parser.add_argument("--out", default="APPS.md", help="Output file (default: APPS.md)")
    args = parser.parse_args()
    Path(args.out).write_text(render(args.repo), encoding="utf-8")
    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
