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

import json
import re
from pathlib import Path
from typing import Any

from src.core.config import TEMP_DIR
from src.core.logger import pr, wpr
from src.core.network import NetworkManager

APKSIGNER: Path = Path("bin/apksigner.jar")
_KNOWN_PREFIXES: tuple[str, ...] = ("gitlab:", "github:")


class PrebuiltsError(Exception):
    pass

def ver_key(ver: str) -> tuple[int, ...]:
    base = ver.partition("-")[0]
    return tuple(int(x) for x in re.findall(r"\d+", base)) or (0,)

def _strip_src_prefix(src: str) -> str:
    for prefix in _KNOWN_PREFIXES:
        if src.startswith(prefix):
            return src.removeprefix(prefix)
    raise PrebuiltsError(f"Unknown source scheme in {src!r}, expected one of {_KNOWN_PREFIXES}")

def get_highest_ver(versions: list[str]) -> str:
    clean = [v.strip() for v in versions if v.strip()]
    if not clean:
        raise ValueError("Empty version list")
    return max(clean, key=ver_key)

def fetch_cli(cli_src: str, cli_ver: str, net: NetworkManager) -> Path:
    cli_org = _strip_src_prefix(cli_src).partition("/")[0]
    cli_dir = TEMP_DIR / cli_org.lower()
    cli_dir.mkdir(parents=True, exist_ok=True)
    jar, changelog = _fetch_single_asset(cli_src, "CLI", cli_ver, "jar", cli_dir, net)
    if changelog:
        with (cli_dir / "changelog.md").open("a", encoding="utf-8") as f:
            f.write(changelog)
    return jar

def fetch_mpp(src: str, ver: str, net: NetworkManager) -> Path:
    org = _strip_src_prefix(src).partition("/")[0]
    cl_dir = TEMP_DIR / org.lower()
    cl_dir.mkdir(parents=True, exist_ok=True)
    mpp, changelog = _fetch_single_asset(src, "Patches", ver, "mpp", cl_dir, net)
    if changelog:
        with (cl_dir / "changelog.md").open("a", encoding="utf-8") as f:
            f.write(changelog)
    return mpp

def _get_target_asset(assets: list[dict[str, Any]], ext: str, src: str, ver: str) -> dict[str, Any]:
    suffix = f".{ext}"
    matches: list[dict[str, Any]] = []
    non_dev: list[dict[str, Any]] = []
    for a in assets:
        name = a.get("name", "")
        if not name.endswith(suffix):
            continue
        matches.append(a)
        if "-dev" not in name:
            non_dev.append(a)

    target = non_dev if (len(matches) > 1 and non_dev) else matches
    if not target:
        raise PrebuiltsError(f"No asset (.{ext}) found for {src} @ {ver}")

    if len(target) > 1:
        wpr(f"More than 1 asset found for {src} @ {ver}, falling back to the first one")
    return target[0]

def _build_changelog(tag: str, org: str, name: str, tag_name: str, gitlab: bool, clean_src: str) -> str:
    changelog = f"> ⚙️ » {tag}: `{org}/{name}`  \n"
    if tag == "Patches" and tag_name:
        if gitlab:
            changelog += f"[🔗 » Changelog](https://gitlab.com/{clean_src}/-/releases/{tag_name})\n\n"
        else:
            changelog += f"[🔗 » Changelog](https://github.com/{clean_src}/releases/tag/{tag_name})\n\n"
    return changelog

def _releases_url(src: str) -> tuple[str, bool]:
    gitlab = src.startswith("gitlab:")
    clean_src = _strip_src_prefix(src)
    if gitlab:
        return f"https://gitlab.com/api/v4/projects/{clean_src.replace('/', '%2F')}/releases", True
    return f"https://api.github.com/repos/{clean_src}/releases", False

def _resolve_release(src: str, ver: str, net: NetworkManager) -> tuple[str, dict[str, Any]]:
    """(tag, release) for a version spec. The release object comes back when resolving it
    already fetched it ('latest'), so the caller does not ask the API for it twice."""
    if ver not in ("dev", "latest"):
        return ver, {}

    base_url, gitlab = _releases_url(src)
    if ver == "dev":
        releases = json.loads(net.get(base_url) if gitlab else net.get(base_url, headers=net.gh_headers))
        return get_highest_ver([r["tag_name"] for r in releases if r.get("tag_name")]), {}

    latest_url = f"{base_url}/permalink/latest" if gitlab else f"{base_url}/latest"
    release = json.loads(net.get(latest_url) if gitlab else net.get(latest_url, headers=net.gh_headers))
    if not (tag_name := release.get("tag_name", "")):
        raise PrebuiltsError(f"No latest release found for {src}")
    return str(tag_name), release

def resolve_release_tag(src: str, ver: str, net: NetworkManager) -> str:
    """The concrete release tag a version spec means right now: 'dev' is the highest tag of
    any release, 'latest' the newest stable release, anything else is already a tag."""
    return _resolve_release(src, ver, net)[0]

def _fetch_single_asset(src: str, tag: str, ver: str, ext: str, cl_dir: Path, net: NetworkManager) -> tuple[Path, str]:
    clean_src = _strip_src_prefix(src)
    org = clean_src.partition("/")[0]
    base_url, gitlab = _releases_url(src)

    ver, release = _resolve_release(src, ver, net)

    if file := _find_cached(cl_dir, ver, ext):
        tag_name = _tag_from_filename(file)
        return file, _build_changelog(tag, org, file.name, tag_name, gitlab, clean_src)

    if not release:
        release_url = f"{base_url}/{ver}" if gitlab else f"{base_url}/tags/{ver}"
        release = json.loads(net.get(release_url) if gitlab else net.get(release_url, headers=net.gh_headers))

    raw_assets = release.get("assets", {}).get("links", []) if gitlab else release.get("assets", [])
    asset = _get_target_asset(raw_assets, ext, src, ver)
    file = cl_dir / asset["name"]
    for old_file in cl_dir.glob(f"*.{ext}"):
        if old_file.is_file() and not old_file.name.startswith("tmp."):
            old_file.unlink(missing_ok=True)

    if gitlab:
        asset_url = asset.get("direct_asset_url") or asset["url"]
        pr(f"Getting '{asset['name']}' from '{asset_url}'")
        net.download(asset_url, file)
    else:
        # The public download link is not an API call, so it does not count against the
        # Actions token's hourly API limit - which a full rebuild of every app would hit.
        asset_url = asset.get("browser_download_url") or asset["url"]
        pr(f"Getting '{asset['name']}' from '{asset_url}'")
        headers = {} if asset.get("browser_download_url") else net.gh_headers | {"Accept": "application/octet-stream"}
        net.download(asset_url, file, headers=headers)

    tag_name = release.get("tag_name", "")
    return file, _build_changelog(tag, org, asset["name"], tag_name, gitlab, clean_src)

def _find_cached(dir_path: Path, name_ver: str, ext: str) -> Path | None:
    pattern = f"*.{ext}" if name_ver == "*" else f"*{name_ver.lstrip('v')}*.{ext}"
    candidates: list[Path] = []
    for path in dir_path.glob(pattern):
        if not path.is_file() or path.name.startswith("tmp."):
            continue
        candidates.append(path)
    return max(candidates, key=lambda p: ver_key(p.name), default=None)

def _tag_from_filename(file: Path) -> str:
    if m := re.search(r"-(\d[\w.]*)(?:-[^.]+)?\.\w+$", file.name):
        return f"v{m.group(1)}"
    return ""
