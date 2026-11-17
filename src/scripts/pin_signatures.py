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
# Added in the morphe-autobuilder-v2 fork: fills sig.txt with the official
# signing certificate of every app in config.toml that is not pinned yet, so
# the builder can refuse a tampered stock APK before patching it.
#
# APKMirror prints each upload's certificate SHA-256 and SHA-1. Where APKPure
# also lists the app, its own record of the certificate (SHA-1) must agree, or
# the app is left unpinned: two stores independently naming the same key is the
# evidence. Apps on neither store stay unpinned and only get a warning at build
# time (strict-sigcheck = false).
#
#   python -m src.scripts.pin_signatures [--write]

import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin

from src.core.config import (
    CONFIG_PATH,
    AppEntry,
    load_toml,
    parse_app_entries,
    parse_config,
)
from src.core.logger import epr, pr, wpr
from src.core.network import NetworkError, NetworkManager

SIG_FILE = Path("sig.txt")
_PAUSE = 4.0           # seconds between apps: APKMirror answers 429 to a fast crawl
_MAX_REFUSALS = 3      # stop after this many apps in a row could not be read
_APKPURE_API = "https://tapi.pureapk.com/v3/get_app_his_version"
_APKPURE_HEADERS = {"Ual-Access-Businessid": "projecta", "Ual-Access-ProjectA": '{"device_info":{"os_ver":"36"}}'}
_PKG_FROM_URL = re.compile(r"/([A-Za-z][\w]*(?:\.[\w]+)+)/?$")


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))

def _apkmirror_cert(app_url: str, net: NetworkManager) -> tuple[str, str, str] | None:
    """(package, sha256, sha1) from the newest upload on an APKMirror app page."""
    page = net.get(app_url)
    pkg_m = re.search(r"play\.google\.com/store/apps/details\?id=([\w.]+)", page)
    rel = re.search(r'href="(/apk/[^"]+-release/)"', page)
    if not (pkg_m and rel):
        return None
    release = net.get(urljoin("https://www.apkmirror.com", rel.group(1)))
    variant = re.search(r'href="(/apk/[^"]+-(?:android-apk|android-apk-bundle)-download/)"', release)
    detail = net.get(urljoin("https://www.apkmirror.com", variant.group(1))) if variant else release
    text = _text(detail)
    sha256 = re.search(r"SHA-256: ([0-9a-f]{64})", text)
    sha1 = re.search(r"SHA-1: ([0-9a-f]{40})", text)
    if not sha256:
        return None
    return pkg_m.group(1), sha256.group(1), sha1.group(1) if sha1 else ""

def _apkpure_sha1(pkg: str, net: NetworkManager) -> str:
    try:
        data = json.loads(net.get(f"{_APKPURE_API}?package_name={pkg}&hl=en", headers=_APKPURE_HEADERS))
    except (NetworkError, json.JSONDecodeError):
        return ""
    for entry in data.get("version_list") or []:
        if entry.get("package_name") == pkg and entry.get("sign"):
            return str(entry["sign"][0]).lower()
    return ""

def _package_hint(entry: AppEntry) -> str:
    url = entry.dl_urls.get("apkpure", "")
    m = _PKG_FROM_URL.search(url)
    return m.group(1) if m else ""

def pin(write: bool) -> None:
    data = load_toml(CONFIG_PATH)
    entries = [e for e in parse_app_entries(data, parse_config(data)) if e.enabled and not e.skip_sigcheck]
    lines = SIG_FILE.read_text(encoding="utf-8").splitlines() if SIG_FILE.exists() else []
    pinned = {ln.split()[-1] for ln in lines if ln.split()}

    added: list[str] = []
    seen: set[str] = set()
    refusals = 0

    def record(line: str) -> None:
        added.append(line)
        if write:  # one line at a time, so an interrupted run keeps what it found
            text = SIG_FILE.read_text(encoding="utf-8") if SIG_FILE.exists() else ""
            with SIG_FILE.open("a", encoding="utf-8") as fh:
                fh.write(("\n" if text and not text.endswith("\n") else "") + line + "\n")

    with NetworkManager() as net:
        for e in entries:
            hint = _package_hint(e)
            if hint and (hint in pinned or hint in seen):
                continue
            url = e.dl_urls.get("apkmirror")
            if not url:
                if hint and (sha1 := _apkpure_sha1(hint, net)):
                    wpr(f"{hint}: only APKPure knows this app; pinning its SHA-1 from a single source")
                    record(f"{sha1} {hint}")
                    seen.add(hint)
                else:
                    wpr(f"{e.table}: no APKMirror page and no APKPure record - left unpinned")
                continue
            if refusals >= _MAX_REFUSALS:
                epr(f"APKMirror refused {refusals} apps in a row; stopping - run again later to pin the rest")
                break
            time.sleep(_PAUSE)
            try:
                found = _apkmirror_cert(url, net)
                refusals = 0
            except NetworkError as exc:
                refusals += 1
                epr(f"{e.table}: APKMirror unreachable ({exc}) - left unpinned")
                continue
            if not found:
                wpr(f"{e.table}: no certificate on APKMirror - left unpinned")
                continue
            pkg, sha256, sha1 = found
            if pkg in pinned or pkg in seen:
                continue
            seen.add(pkg)
            other = _apkpure_sha1(pkg, net)
            if other and sha1 and other != sha1:
                epr(f"{pkg}: APKMirror SHA-1 {sha1} and APKPure SHA-1 {other} disagree - left unpinned, check by hand")
                continue
            pr(f"{pkg}: {sha256}" + (" (APKPure agrees)" if other else ""))
            record(f"{sha256} {pkg}")

    pr(f"{len(added)} new pins" + (f" written to {SIG_FILE}" if write else ""))

def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m src.scripts.pin_signatures", description="Pin the official signing certificate of every app in config.toml.")
    parser.add_argument("--write", action="store_true", help="Append the new pins to sig.txt (default: print them only)")
    pin(parser.parse_args().write)

if __name__ == "__main__":
    main()
