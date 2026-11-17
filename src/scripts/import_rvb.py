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
# Added in the morphe-autobuilder-v2 fork: imports the app catalog of
# nullcpy/rvb (GPLv3), whose per-app TOMLs live on its `data` branch, into
# config.toml. Only apps this builder can produce are taken: Morphe-format
# (.mpp) patch bundles on GitHub/GitLab, downloadable from APKMirror, Uptodown
# or APKPure. Everything goes between two marker lines, so a rerun replaces the
# imported block and never touches hand-written entries.
#
#   GITHUB_TOKEN=... python -m src.scripts.import_rvb [--write]

import argparse
import json
import os
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote

from src.core.config import CONFIG_PATH
from src.core.network import NetworkError, NetworkManager

RVB_REPO = "nullcpy/rvb"
RVB_BRANCH = "data"
RVB_DIR = "configs/patches"
BEGIN = "# >>> imported from nullcpy/rvb - regenerate with `python -m src.scripts.import_rvb --write` >>>"
END = "# <<< imported from nullcpy/rvb <<<"

# Patch sources this config already builds by hand, with the brand they use there.
KNOWN_BRANDS: dict[str, tuple[str, str]] = {
    "github:MorpheApp/morphe-patches": ("Morphe", ""),
    "github:crimera/piko": ("Piko", ""),
    "github:anddea/revanced-patches": ("revanced-extended", "ReVanced Extended"),
}
# rvb's default is "both": apps with native code are only published as per-ABI APKs, which a
# universal ("all") build cannot download.
_ARCH = {"arm-v7a": "armeabi-v7a", "arm64-v8a": "arm64-v8a", "x86": "x86", "x86_64": "x86_64", "all": "all", "auto": "both", "both": "both"}
_NOISE = {"morphe", "patches", "patch", "revanced", "the", "for", "mod", "mods"}


@dataclass
class SourceInfo:
    spec: str          # "github:owner/repo"
    has_stable: bool = False
    has_mpp: bool = False
    error: str = ""

@dataclass
class Report:
    imported: list[str] = field(default_factory=list)
    skipped: dict[str, list[str]] = field(default_factory=dict)

    def skip(self, reason: str, what: str) -> None:
        self.skipped.setdefault(reason, []).append(what)


def _quoted_list(value: Any) -> list[str]:
    """rvb's "'A' 'B'" lists (patch names, sources, hosts)."""
    if isinstance(value, list):
        return [str(v) for v in value]
    return re.findall(r"'([^']*)'", str(value or "")) or ([str(value).strip()] if str(value or "").strip() else [])

def _per_source(value: Any, n: int) -> list[list[str]]:
    """Split an included/excluded-patches value into one list per patch source ('|' separated)."""
    parts = str(value or "").split("|") if n > 1 else [str(value or "")]
    parts += [""] * (n - len(parts))
    return [_quoted_list(p) for p in parts[:n]]

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def _toml(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(_toml(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{ " + ", ".join(f"{k} = {_toml(v)}" for k, v in value.items()) + " }"
    return json.dumps(str(value), ensure_ascii=False)

def _load_rvb(net: NetworkManager) -> list[dict[str, Any]]:
    tree = json.loads(net.get(f"https://api.github.com/repos/{RVB_REPO}/git/trees/{RVB_BRANCH}?recursive=1", headers=net.gh_headers))
    files = sorted(t["path"] for t in tree["tree"] if t["path"].startswith(RVB_DIR + "/") and t["path"].endswith(".toml"))
    apps: list[dict[str, Any]] = []
    for path in files:
        data = tomllib.loads(net.get(f"https://raw.githubusercontent.com/{RVB_REPO}/{RVB_BRANCH}/{quote(path)}"))
        defaults = {k: v for k, v in data.items() if not isinstance(v, dict)}
        for table, cfg in data.items():
            if isinstance(cfg, dict):
                apps.append(defaults | cfg | {"_table": table, "_file": Path(path).name})
    return apps

def _source_specs(app: dict[str, Any]) -> list[str]:
    sources = _quoted_list(app.get("patches-source", "MorpheApp/morphe-patches"))
    hosts = _quoted_list(app.get("patches-source-host", "github")) or ["github"]
    hosts += [hosts[-1]] * (len(sources) - len(hosts))
    return [f"{h}:{s}" for h, s in zip(hosts, sources, strict=False)]

def _inspect_source(spec: str, net: NetworkManager) -> SourceInfo:
    info = SourceInfo(spec)
    host, _, repo = spec.partition(":")
    try:
        if host == "github":
            rels = json.loads(net.get(f"https://api.github.com/repos/{repo}/releases?per_page=30", headers=net.gh_headers))
            rels = [r for r in rels if not r.get("draft")]
            info.has_stable = any(not r.get("prerelease") for r in rels)
            newest = [r for r in rels if not r.get("prerelease")] or rels
            info.has_mpp = bool(newest) and any(a["name"].endswith(".mpp") for a in newest[0].get("assets", []))
        elif host == "gitlab":
            rels = json.loads(net.get(f"https://gitlab.com/api/v4/projects/{quote(repo, safe='')}/releases?per_page=30"))
            info.has_stable = any(not r.get("upcoming_release") for r in rels)
            info.has_mpp = bool(rels) and any(link["name"].endswith(".mpp") for link in rels[0]["assets"]["links"])
        else:
            info.error = f"{host} hosting is not supported"
    except (NetworkError, json.JSONDecodeError, KeyError) as exc:
        info.error = f"unreachable ({exc})"
    return info

def _brands(specs: set[str], apps: list[dict[str, Any]]) -> dict[str, tuple[str, str]]:
    """One brand slug per patch source: rvb's own brand name when only that source uses it,
    else the owner, else owner plus the meaningful part of the repo name."""
    brand_users: dict[str, set[str]] = {}
    brand_names: dict[str, str] = {}
    for app in apps:
        if app.get("brand"):
            brand_users.setdefault(_slug(str(app["brand"])), set()).update(_source_specs(app)[:1])
            brand_names.setdefault(_slug(str(app["brand"])), str(app["brand"]))
    taken = {_slug(b) for b, _ in KNOWN_BRANDS.values()}
    out = dict(KNOWN_BRANDS)
    by_owner: dict[str, list[str]] = {}
    for spec in sorted(specs):
        by_owner.setdefault(spec.partition(":")[2].split("/")[0].lower(), []).append(spec)
    for spec in sorted(specs):
        if spec in out:
            continue
        owner, _, repo = spec.partition(":")[2].partition("/")
        rvb_brand = next((b for b, users in brand_users.items() if users == {spec}), "")
        repo_part = "-".join(w for w in _slug(repo).split("-") if w not in _NOISE and w != _slug(owner))
        for candidate in (rvb_brand, _slug(owner) if len(by_owner[owner.lower()]) == 1 else "", f"{_slug(owner)}-{repo_part}".strip("-"), _slug(f"{owner}-{repo}")):
            if candidate and candidate not in taken:
                # Keep rvb's spelling ("HushFacebook") for the release title when it is more than a recase.
                name = brand_names.get(candidate, "") if candidate == rvb_brand else ""
                keep = name and any(c.isupper() for c in name) and name != candidate.replace("-", " ").title()
                out[spec] = (candidate, name if keep else "")
                taken.add(candidate)
                break
    return out

def _existing_packages(config_text: str) -> dict[str, set[str]]:
    """Packages the hand-written part of config.toml already builds, per brand (lowercase)."""
    head = config_text.split(BEGIN)[0]
    data = tomllib.loads(head)
    have: dict[str, set[str]] = {}
    for cfg in data.values():
        if isinstance(cfg, dict) and (m := re.search(r"/([A-Za-z][\w]*(?:\.[\w]+)+)/?$", str(cfg.get("apkpure-dlurl", "")))):
            have.setdefault(str(cfg.get("brand", "Morphe")).lower(), set()).add(m.group(1))
    return have

def convert(net: NetworkManager) -> tuple[str, Report]:
    report = Report()
    apps = _load_rvb(net)
    config_text = CONFIG_PATH.read_text(encoding="utf-8")
    have = _existing_packages(config_text)
    hand_tables = {k for k, v in tomllib.loads(config_text.split(BEGIN)[0]).items() if isinstance(v, dict)}

    specs = {s for a in apps for s in _source_specs(a)}
    infos = {s: _inspect_source(s, net) for s in sorted(specs)}
    brands = _brands(specs, apps)

    blocks: dict[str, list[str]] = {}
    for app in apps:
        label = f"{app['_file']}:{app['_table']}"
        if not app.get("enabled", True):
            report.skip("disabled in rvb", label)
            continue
        if cli := app.get("cli-source"):
            report.skip(f"needs another patcher ({cli})", label)
            continue
        app_specs = _source_specs(app)
        bad = [s for s in app_specs if infos[s].error or not infos[s].has_mpp]
        if bad:
            why = infos[bad[0]].error or "no .mpp bundle (not Morphe format)"
            report.skip(why, f"{label} ({bad[0]})")
            continue

        brand, brand_title = brands[app_specs[0]]
        pkg = str(app.get("pkg-name", ""))
        variant = " ".join(str(app[k]) for k in ("variant", "sub-variant") if app.get(k))
        if pkg in have.get(brand.lower(), set()) and variant.lower() in ("", "experimental"):
            report.skip("already built by the hand-written config", label)
            continue
        if app["_table"] in hand_tables:
            app["_table"] = f"{app['_table']}-{brand}"

        dl = {}
        for src in ("apkmirror", "uptodown", "apkpure"):
            if url := app.get(f"{src}-dlurl"):
                dl[f"{src}-dlurl"] = re.sub(r"^https?://(?:www\.)?apkmirror\.com", "https://www.apkmirror.com", str(url))
        if not dl:
            report.skip("no APKMirror/Uptodown/APKPure link", label)
            continue

        versions = _quoted_list(app.get("patches-version", "stable")) or ["stable"]
        versions += [versions[-1]] * (len(app_specs) - len(versions))
        unbalanced = False
        for key in ("included-patches", "excluded-patches"):
            if str(app.get(key, "")).count("'") % 2:
                # rvb typo of the form "'A 'B'": the closing quote of A is missing.
                app[key] = re.sub(r"(?<=[^'\s]) '(?=[^\s'])", "' '", str(app[key]))
                unbalanced |= app[key].count("'") % 2 == 1
        if unbalanced:
            report.skip("unbalanced quotes in rvb's patch list - fix by hand", label)
            continue
        includes = _per_source(app.get("included-patches"), len(app_specs))
        excludes = _per_source(app.get("excluded-patches"), len(app_specs))

        patches: dict[str, Any] = {}
        for spec, ver, inc, exc in zip(app_specs, versions, includes, excludes, strict=True):
            if ver in ("stable", "both"):
                ver = "latest" if infos[spec].has_stable else "dev"
            elif ver == "beta":
                ver = "dev"
            patches[spec] = {"version": ver, "include": inc, "exclude": exc} if (ver != "latest" or exc) else inc

        app_name = " ".join(filter(None, [str(app.get("app-name") or app["_table"]), variant]))
        lines = [f"[{app['_table']}]", f"app-name = {_toml(app_name)}", f"brand = {_toml(brand)}"]
        if brand_title:
            lines.append(f"brand-title = {_toml(brand_title)}")
        lines.append(f"arch = {_toml(_ARCH.get(str(app.get('arch', 'both')), 'both'))}")
        if app.get("version") and str(app["version"]) != "auto":
            lines.append(f"version = {_toml(app['version'])}")
        if app.get("dpi"):
            dpi = [d for d in str(app["dpi"]).split() if d != "auto"]
            lines.append(f"dpi = {_toml(','.join(dpi) if dpi else 'all')}")
        if args := app.get("patcher-args"):
            lines.append(f"patcher-args = {_toml(args)}")
        if str(app.get("exclusive-patches", "false")).lower() not in ("false", ""):
            lines.append("exclusive-patches = true")
        if app.get("inclusive-patches") is True:
            lines.append("inclusive-patches = true")
        lines += [f"{k} = {_toml(v)}" for k, v in dl.items()]
        lines += ["", f"[{app['_table']}.patches]"] + [f"{_toml(s)} = {_toml(v)}" for s, v in patches.items()]
        blocks.setdefault(brand, []).append("\n".join(lines))
        report.imported.append(label)

    out = [BEGIN, f"# {len(report.imported)} apps from https://github.com/{RVB_REPO}/tree/{RVB_BRANCH}/{RVB_DIR} (GPLv3)", ""]
    for brand in sorted(blocks, key=str.lower):
        source = next(s for s, (b, _) in brands.items() if b == brand)
        out += [f"# ---- {brand}: {source} ----", ""]
        out += [b + "\n" for b in blocks[brand]]
    out.append(END)
    return "\n".join(out) + "\n", report

def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m src.scripts.import_rvb", description="Import nullcpy/rvb's app catalog into config.toml.")
    parser.add_argument("--write", action="store_true", help="Write the imported block into config.toml (default: print a report only)")
    args = parser.parse_args()
    if not os.getenv("GITHUB_TOKEN"):
        parser.error("set GITHUB_TOKEN: the import makes more GitHub API calls than the anonymous limit allows")

    with NetworkManager() as net:
        block, report = convert(net)

    print(f"Imported: {len(report.imported)}")
    for reason, items in sorted(report.skipped.items(), key=lambda kv: -len(kv[1])):
        print(f"Skipped ({reason}): {len(items)}")
        for item in items:
            print(f"    {item}")

    if args.write:
        text = CONFIG_PATH.read_text(encoding="utf-8")
        head = text.split(BEGIN)[0].rstrip() + "\n\n"
        tail = text.split(END, 1)[1].lstrip() if END in text else ""
        CONFIG_PATH.write_text(head + block + tail, encoding="utf-8")
        print(f"Wrote {CONFIG_PATH}")
        from src.scripts.workflow_choices import sync
        sync()  # new brands must also appear in the "Run workflow" dropdowns

if __name__ == "__main__":
    main()
