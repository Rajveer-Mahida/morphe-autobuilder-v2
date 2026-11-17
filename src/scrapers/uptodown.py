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
# Added in the morphe-autobuilder-v2 fork: Uptodown download source, ported from
# the GPLv3 morphe-autobuilder (nullcpy/rvb) scripts/uptodown.py.
#
# Versions and per-ABI variants come from the public web pages. The download link
# itself is minted by the Uptodown Android app API: an HMAC-signed request returns
# a bearer token, which then exchanges a file id for a signed CDN URL.

import hashlib
import hmac
import json
import re
import secrets
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, override

from bs4 import Tag

from src.core.logger import wpr
from src.core.network import NetworkManager
from src.scrapers.arch import abi_matches, parse_abis
from src.scrapers.base import (
    AppMetadata,
    BaseScraper,
    DownloadResult,
    ScraperError,
    parse_html,
)

_API = "https://www.uptodown.app/eapi"
_APP_HEADERS: dict[str, str] = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 16; Pixel 8 Pro Build/BP4A.260205.001)",
    "Identificador": "Uptodown_Android",
    "Identificador-Version": "739",
}
_HMAC_KEY = b"MDGMXUMdvHJBG/vjdFgmqX6LUdy7ecfwvYNd0gyfOCs="
_MAX_VERSION_PAGES = 15
_PRERELEASE_WORDS = ("beta", "alpha", "secondary")


class UptodownError(ScraperError):
    pass

@dataclass(slots=True, frozen=True)
class _Variant:
    file_id: str
    version: str
    abis: frozenset[str]
    is_bundle: bool

class UptodownScraper(BaseScraper):
    """Accepts an Uptodown app URL, e.g. https://youtube-music.en.uptodown.com/android"""

    def __init__(self, net: NetworkManager) -> None:
        super().__init__(net)
        self._app_ids: dict[str, str] = {}

    @staticmethod
    def _clean(url: str) -> str:
        url = url.rstrip("/")
        for suffix in ("/versions", "/download", "/files"):
            url = url.removesuffix(suffix)
        return url

    def _app_id(self, base: str) -> str:
        if base not in self._app_ids:
            html = self.net.get(base)
            m = re.search(r'id="detail-app-name"[^>]*data-code="(\d+)"', html) or re.search(r'data-code="(\d+)"', html)
            if not m:
                raise UptodownError(f"No app id on {base}")
            self._app_ids[base] = m.group(1)
        return self._app_ids[base]

    def _version_page(self, base: str, app_id: str, page: int) -> list[dict[str, Any]]:
        try:
            data = json.loads(self.net.get(f"{base}/apps/{app_id}/versions/{page}"))
        except json.JSONDecodeError as exc:
            raise UptodownError(f"Unreadable version list page {page}") from exc
        return list(data.get("data") or [])

    @override
    def fetch_metadata(self, url: str) -> AppMetadata:
        base = self._clean(url)
        app_id = self._app_id(base)

        soup = parse_html(self.net.get(f"{base}/download"))
        pkg = ""
        for th in soup.find_all("th"):
            if th.get_text(strip=True).lower() == "package name" and (td := th.find_next_sibling("td")):
                pkg = td.get_text(strip=True)
                break
        if not pkg:
            raise UptodownError("Package name not found")

        versions: list[str] = []
        for page in range(1, 6):
            items = self._version_page(base, app_id, page)
            if not items:
                break
            for it in items:
                v = str(it.get("version") or "").strip()
                if v and v not in versions and not any(w in v.lower() for w in _PRERELEASE_WORDS):
                    versions.append(v)
        return AppMetadata(pkg_name=pkg, versions=versions)

    def _variants(self, base: str, app_id: str, file_id: str) -> list[_Variant]:
        """Every ABI variant Uptodown lists next to one upload, or [] when it lists none."""
        m = re.search(r'data-version="(\d+)"', self.net.get(f"{base}/download/{file_id}"))
        if not m:
            return []

        origin = base.rsplit("/", 1)[0]
        try:
            content = json.loads(self.net.get(f"{origin}/app/{app_id}/version/{m.group(1)}/files")).get("content") or ""
        except json.JSONDecodeError:
            return []

        variants: list[_Variant] = []
        for box in parse_html(content).select("section.variants div.content"):
            abis: frozenset[str] = frozenset()
            for node in box.children:
                if not isinstance(node, Tag):
                    continue
                if node.name == "p":
                    abis = parse_abis(node.get_text(" ", strip=True))
                elif "variant" in (node.get("class") or []):
                    fid = node.select_one("[data-file-id]")
                    ver = node.select_one(".v-version")
                    kind = node.select_one(".v-file span")
                    if fid and ver:
                        variants.append(_Variant(
                            file_id=str(fid["data-file-id"]),
                            version=ver.get_text(strip=True),
                            abis=abis,
                            is_bundle=kind is not None and kind.get_text(strip=True).lower() != "apk",
                        ))
        return variants

    def _find_upload(self, base: str, app_id: str, version: str) -> list[dict[str, Any]]:
        clean_ver = re.split(r"[\s-]", version.strip(), maxsplit=1)[0]
        for page in range(1, _MAX_VERSION_PAGES + 1):
            items = self._version_page(base, app_id, page)
            if not items:
                break
            if hits := [it for it in items if str(it.get("version") or "").strip() in (version, clean_ver)]:
                return hits
        return []

    def _cdn_url(self, app_id: str, file_id: str) -> str:
        identifier = secrets.token_hex(8)
        ts = str(int(time.time()))
        signature = hmac.new(_HMAC_KEY, ts.encode(), hashlib.sha256).hexdigest()
        body = {"identifier": identifier, "id_plataforma": "13", "lang": "en", "unixtime": ts, "hmac": signature}
        try:
            token = json.loads(self.net.post(f"{_API}/auth/token?identifier={identifier}", data=body, headers=_APP_HEADERS)).get("token")
        except json.JSONDecodeError as exc:
            raise UptodownError("Unreadable auth answer") from exc
        if not token:
            raise UptodownError("Uptodown refused an auth token")

        answer = json.loads(self.net.get(f"{_API}/apps/{app_id}/file/{file_id}/downloadUrl", headers=_APP_HEADERS | {"Authorization": f"Bearer {token}"}))
        url = (answer.get("data") or {}).get("downloadURL")
        if answer.get("success") != 1 or not url:
            raise UptodownError(f"No download URL for file {file_id}: {answer}")
        return str(url)

    @override
    def download(self, url: str, version: str, dest: Path, arch: str, dpi: str, version_code: str | None = None) -> DownloadResult:
        base = self._clean(url)
        app_id = self._app_id(base)
        uploads = self._find_upload(base, app_id, version)
        if not uploads:
            raise UptodownError(f"Version '{version}' not found")

        clean_ver = re.split(r"[\s-]", version.strip(), maxsplit=1)[0]
        variants = [v for v in self._variants(base, app_id, str(uploads[0]["fileID"])) if v.version in (version, clean_ver)]
        if variants:
            fitting = [v for v in variants if abi_matches(v.abis, arch)]
            if not fitting:
                offered = sorted({"+".join(sorted(v.abis)) or "universal" for v in variants})
                raise UptodownError(f"No '{arch}' file for '{version}' (Uptodown offers: {', '.join(offered)})")
            # Prefer the file built for exactly this ABI, then a plain APK over a bundle.
            chosen = min(fitting, key=lambda v: (v.abis != {arch}, v.is_bundle))
            file_id, is_bundle = chosen.file_id, chosen.is_bundle
        else:
            if len(uploads) > 1:
                wpr(f"Uptodown lists {len(uploads)} uploads of '{version}' without ABI labels; taking the newest")
            file_id, is_bundle = str(uploads[0]["fileID"]), uploads[0].get("kindFile") == "xapk"

        out_path = dest.with_suffix(".xapk") if is_bundle else dest
        self.net.download(self._cdn_url(app_id, file_id), out_path)
        return DownloadResult(path=out_path, is_bundle=is_bundle)
