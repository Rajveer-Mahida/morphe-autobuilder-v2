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
# Added in the morphe-autobuilder-v2 fork: one place that maps a source name to
# its scraper, used by both the builder and the CI matrix script.

from src.core.network import NetworkManager
from src.scrapers.base import BaseScraper


def make_scraper(source: str, net: NetworkManager) -> BaseScraper:
    match source:
        case "apkmirror":
            from src.scrapers.apkmirror import APKMirrorScraper
            return APKMirrorScraper(net)
        case "github":
            from src.scrapers.github import GitHubScraper
            return GitHubScraper(net)
        case "uptodown":
            from src.scrapers.uptodown import UptodownScraper
            return UptodownScraper(net)
        case "apkpure":
            from src.scrapers.apkpure import APKPureScraper
            return APKPureScraper(net)
        case _:
            raise ValueError(f"Unknown APK source: {source!r}")
