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
# Added in the morphe-autobuilder-v2 fork: prints the Obtainium "Import config"
# links used in README.md. Add an app to APPS and paste the output over the
# link block at the bottom of the README.
#
#   python -m src.scripts.obtainium --repo owner/name

import argparse
import json
import re
from dataclasses import dataclass
from urllib.parse import quote


@dataclass(frozen=True, slots=True)
class ObtainiumApp:
    ref: str          # markdown link reference used in README.md
    app_id: str       # package name of the installed (patched) app
    name: str         # name shown in Obtainium
    brand: str        # patch source: release titles are "<Brand> Patches v<version>"
    row: str          # app name in the release notes' download table
    asset: str        # APK file name prefix in the release assets

APPS: tuple[ObtainiumApp, ...] = (
    ObtainiumApp("yt-morphe", "app.morphe.android.youtube", "YouTube", "Morphe", "YouTube", "youtube-morphe-v"),
    ObtainiumApp("yt-exp-morphe", "app.morphe.android.youtube", "YouTube Experimental", "Morphe", "YouTube Experimental", "youtube-experimental-morphe-v"),
    ObtainiumApp("music-morphe", "app.morphe.android.apps.youtube.music", "YouTube Music", "Morphe", "Music", "music-morphe-v"),
    ObtainiumApp("music-exp-morphe", "app.morphe.android.apps.youtube.music", "YouTube Music Experimental", "Morphe", "Music Experimental", "music-experimental-morphe-v"),
    ObtainiumApp("reddit-morphe", "com.reddit.frontpage", "Reddit", "Morphe", "Reddit", "reddit-morphe-v"),
    ObtainiumApp("reddit-exp-morphe", "com.reddit.frontpage", "Reddit Experimental", "Morphe", "Reddit Experimental", "reddit-experimental-morphe-v"),
    ObtainiumApp("x-piko", "com.twitter.android", "X", "Piko", "X", "x-piko-v"),
    ObtainiumApp("twitter-piko", "com.twitter.android", "Twitter", "Piko", "Twitter", "twitter-piko-v"),
    ObtainiumApp("instagram-piko", "com.instagram.android", "Instagram", "Piko", "Instagram", "instagram-piko-v"),
    ObtainiumApp("yt-rvx", "anddea.youtube", "YouTube ReVanced Extended", "ReVanced Extended", "YouTube", "youtube-revanced-extended-v"),
    ObtainiumApp("music-rvx", "anddea.youtube.music", "YouTube Music ReVanced Extended", "ReVanced Extended", "YouTube Music", "youtube-music-revanced-extended-v"),
    ObtainiumApp("jiohotstar-chiggi", "in.startv.hotstar", "JioHotstar TV", "Chiggi", "JioHotstar TV", "jiohotstar-tv-chiggi-v"),
    ObtainiumApp("jiotv-chiggi", "com.jio.media.jiotvplus", "JioTV Plus TV", "Chiggi", "JioTV Plus TV", "jiotv-plus-tv-chiggi-v"),
    ObtainiumApp("threads-chiggi", "com.instagram.barcelona", "Threads", "Chiggi", "Threads", "threads-chiggi-v"),
)


def _settings(app: ObtainiumApp) -> dict[str, object]:
    return {
        "includePrereleases": False,
        "fallbackToOlderReleases": True,
        # Only this source's releases ...
        "filterReleaseTitlesByRegEx": f"^{re.escape(app.brand)} Patches v",
        # ... that contain this exact app (its own row in the download table, so
        # "YouTube" does not also match a release holding only "YouTube Experimental").
        "filterReleaseNotesByRegEx": rf"\| {re.escape(app.row)} \|",
        "verifyLatestTag": False,
        "sortMethodChoice": "date",
        "useLatestAssetDateAsReleaseDate": False,
        "releaseTitleAsVersion": False,
        "trackOnly": False,
        "versionExtractionRegEx": "",
        "matchGroupToUse": "",
        "versionDetection": False,
        "releaseDateAsVersion": False,
        "useVersionCodeAsOSVersion": False,
        "apkFilterRegEx": f"^{re.escape(app.asset)}",
        "invertAPKFilter": False,
        "autoApkFilterByArch": True,
        "appName": app.name,
        "appAuthor": "",
        "shizukuPretendToBeGooglePlay": False,
        "allowInsecure": False,
        "exemptFromBackgroundUpdates": False,
        "skipUpdateNotifications": False,
        "about": "",
        "refreshBeforeDownload": False,
        "includeZips": False,
        "zippedApkFilterRegEx": "",
        "dontSortReleasesList": False,
        "github-creds": "",
    }

def import_link(app: ObtainiumApp, repo: str) -> str:
    owner = repo.partition("/")[0]
    config = {
        "id": app.app_id,
        "url": f"https://github.com/{repo}",
        "author": owner,
        "name": app.name,
        "preferredApkIndex": 0,
        "additionalSettings": json.dumps(_settings(app), separators=(",", ":")),
        "overrideSource": "GitHub",
    }
    payload = quote(json.dumps(config, separators=(",", ":")), safe="")
    return f"https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/{payload}"

def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m src.scripts.obtainium", description="Print the Obtainium import links for README.md.")
    parser.add_argument("--repo", required=True, help="GitHub repository the configs point at, as owner/name")
    args = parser.parse_args()
    print("<!-- Obtainium import links: generated by `python -m src.scripts.obtainium` -->")
    for app in APPS:
        print(f"[{app.ref}]: {import_link(app, args.repo)}")

if __name__ == "__main__":
    main()
