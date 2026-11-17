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
# Added in the morphe-autobuilder-v2 fork: APKPure download source.
#
# apkpure.com itself sits behind Cloudflare, so this reads the store app's own
# API instead. One call returns the newest ~20 uploads, each with its version
# name and code, the ABIs it carries, its file type (APK or XAPK), a direct CDN
# URL and a SHA-1 - everything needed to pick the right file without HTML.

import hashlib
import json
import re
from pathlib import Path
from typing import Any, override

from src.core.logger import wpr
from src.core.network import NetworkManager
from src.scrapers.arch import abi_matches
from src.scrapers.base import AppMetadata, BaseScraper, DownloadResult, ScraperError

_API_URL = "https://tapi.pureapk.com/v3/get_app_his_version"
_API_HEADERS: dict[str, str] = {
    "Ual-Access-Businessid": "projecta",
    "Ual-Access-ProjectA": '{"device_info":{"os_ver":"36"}}',
}
_PKG_RE = re.compile(r"^[A-Za-z][\w]*(?:\.[A-Za-z][\w]*)+$")
# Same exclusions as the APKMirror scraper: these are not the stable channel the patches target.
_PRERELEASE_WORDS = ("beta", "alpha", "secondary")


class APKPureError(ScraperError):
    pass

class APKPureScraper(BaseScraper):
    """Accepts any apkpure.com app URL, e.g. https://apkpure.com/youtube-music/com.google.android.apps.youtube.music"""

    def __init__(self, net: NetworkManager) -> None:
        super().__init__(net)
        self._entries: dict[str, list[dict[str, Any]]] = {}

    @staticmethod
    def _pkg_from_url(url: str) -> str:
        for part in reversed(url.split("?")[0].rstrip("/").split("/")):
            if _PKG_RE.match(part):
                return part
        raise APKPureError(f"No package name in APKPure URL: {url}")

    def _fetch_entries(self, pkg: str) -> list[dict[str, Any]]:
        if pkg not in self._entries:
            try:
                data = json.loads(self.net.get(f"{_API_URL}?package_name={pkg}&hl=en", headers=_API_HEADERS))
            except json.JSONDecodeError as exc:
                raise APKPureError(f"Unreadable API answer for '{pkg}'") from exc
            if data.get("retcode") != 0:
                raise APKPureError(f"API error for '{pkg}': {data.get('errmsg') or data.get('retcode')}")
            self._entries[pkg] = [e for e in data.get("version_list", []) if e.get("asset", {}).get("url")]
        if not self._entries[pkg]:
            raise APKPureError(f"No downloadable versions listed for '{pkg}'")
        return self._entries[pkg]

    @override
    def fetch_metadata(self, url: str) -> AppMetadata:
        pkg = self._pkg_from_url(url)
        versions: list[str] = []
        for e in self._fetch_entries(pkg):
            v = str(e.get("version_name") or "").strip()
            if v and not e.get("is_beta") and v not in versions and not any(w in v.lower() for w in _PRERELEASE_WORDS):
                versions.append(v)
        return AppMetadata(pkg_name=pkg, versions=versions)

    @override
    def download(self, url: str, version: str, dest: Path, arch: str, dpi: str, version_code: str | None = None) -> DownloadResult:
        pkg = self._pkg_from_url(url)
        clean_ver = re.split(r"[\s-]", version.strip(), maxsplit=1)[0]
        named = [e for e in self._fetch_entries(pkg) if str(e.get("version_name") or "").strip() in (version, clean_ver)]
        if not named:
            raise APKPureError(f"Version '{version}' is not among APKPure's recent uploads")

        if version_code is not None:
            exact = [e for e in named if str(e.get("version_code")) == version_code]
            if exact:
                named = exact
            else:
                wpr(f"APKPure has '{version}' but not versionCode {version_code}; using its own build of that version")

        fitting = [e for e in named if abi_matches(frozenset(e.get("native_code") or []), arch)]
        if not fitting:
            offered = sorted({"+".join(e.get("native_code") or ["universal"]) for e in named})
            raise APKPureError(f"No '{arch}' file for '{version}' (APKPure offers: {', '.join(offered)})")

        # A plain APK needs no merge step, so it wins over an XAPK bundle of the same build.
        entry = min(fitting, key=lambda e: 0 if e["asset"].get("type") == "APK" else 1)
        asset = entry["asset"]
        is_bundle = asset.get("type") != "APK"
        out_path = dest.with_suffix(".xapk") if is_bundle else dest
        self.net.download(asset["url"], out_path)

        if expected := str(asset.get("sha1") or "").lower():
            with out_path.open("rb") as fh:
                digest = hashlib.file_digest(fh, "sha1").hexdigest()
            if digest != expected:
                out_path.unlink(missing_ok=True)
                raise APKPureError(f"SHA-1 mismatch for '{out_path.name}': expected {expected}, got {digest}")
        return DownloadResult(path=out_path, is_bundle=is_bundle)
