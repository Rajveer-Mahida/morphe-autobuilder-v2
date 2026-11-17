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
# Added in the morphe-autobuilder-v2 fork: a cache of stock (unpatched) APKs,
# kept in this same repository as DRAFT releases - one per app:
#
#   release name  = "APK cache: <package>"      (APK cache: com.google.android.youtube)
#   asset name    = <package>-v<version>-<arch>.<apk|apkm|xapk|apks>
#                   (com.google.android.youtube-v20.45.36-all.apkm)
#
# Drafts are visible only to the repository's owner and to workflows, so the
# original apps are never published from here. The builder looks in the cache
# before any store, and uploads every APK it had to download from a store once
# that APK passed the signature check. Files can also be added by hand (edit the
# draft, attach the file, "Save draft") for apps no store carries.
#
# Active in GitHub Actions only, with the workflow's own GITHUB_TOKEN. Listing the
# drafts takes several API calls, so the workflow's prepare job does it once
# (`python -m src.core.apk_cache`) and hands every build job the result in
# APK_CACHE_INDEX.

import json
import os
import sys
import threading
from pathlib import Path
from typing import Any
from urllib.parse import quote

from src.core.logger import pr, wpr
from src.core.network import NetworkError, NetworkManager

_API = "https://api.github.com"
_UPLOADS = "https://uploads.github.com"
_NAME_PREFIX = "APK cache: "
_PAGES = 20  # 2000 releases: published builds plus one draft per cached app
BUNDLE_SUFFIXES: tuple[str, ...] = (".apkm", ".xapk", ".apks")


def asset_name(pkg: str, version: str, arch: str, suffix: str = ".apk") -> str:
    version_f = version.replace(" ", "").lstrip("v")
    return f"{pkg}-v{version_f}-{arch.replace(' ', '')}{suffix}"

def candidates(pkg: str, version: str, arch: str) -> list[str]:
    """File names that satisfy a build, best first: the exact arch, then a universal file."""
    arches = [arch] if arch == "all" else [arch, "all"]
    return [asset_name(pkg, version, a, s) for a in arches for s in (".apk", *BUNDLE_SUFFIXES)]

class ApkCache:
    def __init__(self, net: NetworkManager) -> None:
        self.net = net
        self.repo = os.getenv("GITHUB_REPOSITORY", "")
        token = os.getenv("GITHUB_TOKEN", "")
        self.enabled = os.getenv("GITHUB_ACTIONS") == "true" and bool(self.repo and token) and os.getenv("APK_CACHE", "on") != "off"
        self._headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        self._index: dict[str, dict[str, Any]] | None = None
        self._lock = threading.Lock()

    def list_drafts(self) -> dict[str, dict[str, Any]]:
        """package -> {"id": draft id, "assets": [{"name", "url"}]}, read from the releases API."""
        index: dict[str, dict[str, Any]] = {}
        for page in range(1, _PAGES + 1):
            rels = json.loads(self.net.get(f"{_API}/repos/{self.repo}/releases?per_page=100&page={page}", headers=self._headers))
            for rel in rels:
                name = str(rel.get("name") or "")
                if rel.get("draft") and name.startswith(_NAME_PREFIX):
                    pkg = name.removeprefix(_NAME_PREFIX).strip()
                    assets = [{"name": a["name"], "url": a["url"]} for a in rel.get("assets", [])]
                    # Two jobs may have created a draft at the same moment: keep the fuller one.
                    if len(assets) >= len(index.get(pkg, {}).get("assets", [])):
                        index[pkg] = {"id": rel["id"], "assets": assets}
            if len(rels) < 100:
                break
        return index

    def _load_index(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            if self._index is None:
                handed = os.getenv("APK_CACHE_INDEX", "").strip()
                self._index = json.loads(handed) if handed else self.list_drafts()
            return self._index

    def fetch(self, pkg: str, version: str, arch: str, dest_dir: Path) -> Path | None:
        """Download a cached stock APK into dest_dir, or None when the cache has no match."""
        if not self.enabled:
            return None
        try:
            release = self._load_index().get(pkg)
            if not release:
                return None
            assets = {a["name"]: a for a in release.get("assets", [])}
            name = next((n for n in candidates(pkg, version, arch) if n in assets), None)
            if not name:
                return None
            dest = dest_dir / name
            pr(f"Downloading '{name}' from the APK cache")
            self.net.download(assets[name]["url"], dest, headers=self._headers | {"Accept": "application/octet-stream"})
            return dest
        except (NetworkError, json.JSONDecodeError, KeyError) as exc:
            wpr(f"APK cache lookup failed for '{pkg}' ({exc}); using the stores")
            return None

    def _draft_for(self, pkg: str) -> dict[str, Any]:
        index = self._load_index()
        if pkg in index:
            return index[pkg]
        body = {
            "tag_name": f"apk-cache-{pkg}",
            "name": f"{_NAME_PREFIX}{pkg}",
            "body": f"Stock (unpatched) APKs of `{pkg}`, cached by the builder. Kept as a draft so it is never published.",
            "draft": True,
        }
        resp = self.net.session.post(f"{_API}/repos/{self.repo}/releases", json=body, headers=self._headers, timeout=(5, 30))
        resp.raise_for_status()
        with self._lock:
            index[pkg] = {"id": resp.json()["id"], "assets": []}
        return index[pkg]

    def store(self, path: Path, pkg: str, name: str) -> None:
        """Upload a verified stock APK as `name`. Never raises: a cache problem must not fail a build."""
        if not self.enabled:
            return
        try:
            draft = self._draft_for(pkg)
            if any(a["name"] == name for a in draft.get("assets", [])):
                return
            url = f"{_UPLOADS}/repos/{self.repo}/releases/{draft['id']}/assets?name={quote(name)}"
            headers = self._headers | {"Content-Type": "application/octet-stream"}
            resp = self.net.session.post(url, data=path.read_bytes(), headers=headers, timeout=(10, 600))
            if resp.status_code == 422:  # already uploaded by a parallel job
                return
            resp.raise_for_status()
            draft.setdefault("assets", []).append({"name": name, "url": resp.json()["url"]})
            pr(f"Saved '{name}' to the APK cache")
        except Exception as exc:
            wpr(f"Could not save '{name}' to the APK cache: {exc}")


def main() -> None:
    """Print the cache index as compact JSON (for the workflow's prepare job)."""
    with NetworkManager() as net:
        cache = ApkCache(net)
        if not cache.enabled:
            print("{}")
            return
        try:
            index = cache.list_drafts()
        except (NetworkError, json.JSONDecodeError) as exc:
            print(f"APK cache index unavailable: {exc}", file=sys.stderr)
            index = {}
        print(json.dumps(index, separators=(",", ":")))

if __name__ == "__main__":
    main()
