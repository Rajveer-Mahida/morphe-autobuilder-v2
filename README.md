<div align="center">

# Morphe Autobuilder

**Pre-patched Android apps, rebuilt automatically every time a new patch release ships.**

[![Build](https://img.shields.io/github/actions/workflow/status/Rajveer-Mahida/morphe-autobuilder-v2/ci.yml?style=for-the-badge&logo=githubactions&logoColor=white&label=Build&color=6E40C9)](https://github.com/Rajveer-Mahida/morphe-autobuilder-v2/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/Rajveer-Mahida/morphe-autobuilder-v2?style=for-the-badge&logo=android&logoColor=white&label=Latest&color=6E40C9&sort=date)](https://github.com/Rajveer-Mahida/morphe-autobuilder-v2/releases)
[![Downloads](https://img.shields.io/github/downloads/Rajveer-Mahida/morphe-autobuilder-v2/total?style=for-the-badge&logo=github&logoColor=white&label=Downloads&color=6E40C9)](https://github.com/Rajveer-Mahida/morphe-autobuilder-v2/releases)
[![License](https://img.shields.io/badge/License-GPLv3-6E40C9?style=for-the-badge)](LICENSE)

[**Apps**](#-apps) · [**Install**](#-installation) · [**Verify**](#-verify-your-download) · [**Build your own**](#%EF%B8%8F-build-your-own)

</div>

---

## ✨ Highlights

|  |  |
| :--- | :--- |
| 🛑 **No ads** | Ads and upsell nags patched out, plus extra features from each patch set. |
| ⚡ **Always current** | Checked every day at 10:00 UTC; a new patch release triggers a fresh build. |
| 🔄 **Auto-updates** | One-tap [Obtainium](https://github.com/ImranR98/Obtainium) configs keep every app up to date. |
| 🔐 **One signing key** | Every APK is signed with the same key, so each release installs as an update. |
| 📦 **Right build for your phone** | Separate `arm64-v8a` / `armeabi-v7a` APKs where it saves space, universal where it doesn't. |
| 🔍 **Fully transparent** | Built on public GitHub Actions from this source code - nothing is built by hand. |

## 📱 Apps

Each patch source gets its own releases, named after the patch version they were built from - `morphe-2.3.0`, `piko-3.11.1`.

### 🧩 [Morphe](https://github.com/MorpheApp/morphe-patches) &nbsp;·&nbsp; [All releases](https://github.com/Rajveer-Mahida/morphe-autobuilder-v2/releases?q=morphe-&expanded=true)

| App | Architecture | Obtainium |
| :--- | :---: | :---: |
| **YouTube** | Universal | [Stable][yt-morphe] · [Experimental][yt-exp-morphe] |
| **YouTube Music** | `arm64-v8a` · `armeabi-v7a` | [Stable][music-morphe] · [Experimental][music-exp-morphe] |
| **Reddit** | Universal | [Stable][reddit-morphe] · [Experimental][reddit-exp-morphe] |

### 🧩 [Piko](https://github.com/crimera/piko) &nbsp;·&nbsp; [All releases](https://github.com/Rajveer-Mahida/morphe-autobuilder-v2/releases?q=piko-&expanded=true)

| App | Architecture | Obtainium |
| :--- | :---: | :---: |
| **X** | Universal | [X branding][x-piko] · [Twitter branding][twitter-piko] |
| **Instagram** | `arm64-v8a` | [Import][instagram-piko] |

> [!NOTE]
> **Experimental** builds use the newest app version the patches support, including versions the patch authors still mark as experimental. Pick **Stable** unless you want to try new app releases early.

## 📲 Installation

**With Obtainium (recommended)**

1. Install [Obtainium](https://github.com/ImranR98/Obtainium/releases).
2. Open this page on your phone and tap the app's **Obtainium** link above - the config is imported in one tap.
3. Install from Obtainium. It picks the right APK for your phone's architecture and keeps it updated.

**Manually**

1. Open the [latest release](https://github.com/Rajveer-Mahida/morphe-autobuilder-v2/releases) for the patch source you want.
2. Download the APK for your architecture. Most phones from the last few years are `arm64-v8a`; *Universal* runs on any device.
3. Install it. Allow installs from your browser or file manager if Android asks.

> [!IMPORTANT]
> - **Uninstall any copy of the same app signed by someone else first.** Android refuses to update an app across signing keys.
> - **YouTube and YouTube Music** need [MicroG-RE](https://github.com/MorpheApp/MicroG-RE/releases) installed for Google account sign-in.

## 🔐 Verify your download

Every APK is signed with the same key. Its SHA-256 certificate fingerprint is:

```text
4eae64b769f112a9134bb267fed75d6d8fe0788186455495d0361a404fb2f34a
```

Check any download with [`apksigner`](https://developer.android.com/tools/apksigner) - the fingerprint it prints must match:

```bash
apksigner verify --print-certs app.apk | grep SHA-256
```

On a phone, apps such as [App Manager](https://github.com/MuntashirAkon/AppManager) show the same fingerprint under *Signatures*. The fingerprint is also listed in the *Build details* of every release.

## 🛠️ Build your own

Fork the repository, add your own signing key as Actions secrets, and the same pipeline builds for you. Locally (needs [uv](https://docs.astral.sh/uv/) and Java 21+):

```bash
uv sync
uv run main.py --target YouTube
```

See [**CONTRIBUTING.md**](CONTRIBUTING.md) for every config option, adding apps and patch sources, and setting up a signing key.

## ⚖️ License & credits

Released under the **GNU GPLv3** - see [LICENSE](LICENSE).

- **Based on [uni-apks](https://github.com/krvstek/uni-apks)** by [krvstek](https://github.com/krvstek), **Copyright (C) 2026 krvstek**. Original copyright notices are kept in every source file; contributors are listed in [AUTHORS](AUTHORS).
- **Uptodown downloader** ported from [nullcpy/rvb](https://github.com/nullcpy/rvb) (GPLv3).
- **Original build approach** by [j-hc](https://github.com/j-hc).
- **Icons** based on designs by [kazimmt](https://github.com/kazimmt) - see [icons/README.md](icons/README.md).
- **Patches** by [MorpheApp](https://github.com/MorpheApp) and [crimera](https://github.com/crimera). Please star and support their work.

## ⚠️ Disclaimer

This project is not affiliated with Google, Reddit, X Corp., Meta or any patch author. It only automates building with publicly available tools, for personal and educational use. If a build breaks after an app or patch update, it is usually fixed upstream - please report patch bugs to the patch authors.

---

<div align="center">

<a href="https://github.com/Rajveer-Mahida"><img src="https://github.com/Rajveer-Mahida.png?size=120" width="64" height="64" alt="Rajveer Mahida"></a>

**Maintained by [Rajveer Mahida](https://github.com/Rajveer-Mahida)**

If these builds save you time, a ⭐ on the repo helps others find them.

</div>

<!-- Obtainium import links: generated by `python -m src.scripts.obtainium` -->
[yt-morphe]: https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22app.morphe.android.youtube%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FRajveer-Mahida%2Fmorphe-autobuilder-v2%22%2C%22author%22%3A%22Rajveer-Mahida%22%2C%22name%22%3A%22YouTube%22%2C%22preferredApkIndex%22%3A0%2C%22additionalSettings%22%3A%22%7B%5C%22includePrereleases%5C%22%3Afalse%2C%5C%22fallbackToOlderReleases%5C%22%3Atrue%2C%5C%22filterReleaseTitlesByRegEx%5C%22%3A%5C%22%5EMorphe%20Patches%20v%5C%22%2C%5C%22filterReleaseNotesByRegEx%5C%22%3A%5C%22%5C%5C%5C%5C%7C%20YouTube%20%5C%5C%5C%5C%7C%5C%22%2C%5C%22verifyLatestTag%5C%22%3Afalse%2C%5C%22sortMethodChoice%5C%22%3A%5C%22date%5C%22%2C%5C%22useLatestAssetDateAsReleaseDate%5C%22%3Afalse%2C%5C%22releaseTitleAsVersion%5C%22%3Afalse%2C%5C%22trackOnly%5C%22%3Afalse%2C%5C%22versionExtractionRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22matchGroupToUse%5C%22%3A%5C%22%5C%22%2C%5C%22versionDetection%5C%22%3Afalse%2C%5C%22releaseDateAsVersion%5C%22%3Afalse%2C%5C%22useVersionCodeAsOSVersion%5C%22%3Afalse%2C%5C%22apkFilterRegEx%5C%22%3A%5C%22%5Eyoutube%5C%5C%5C%5C-morphe%5C%5C%5C%5C-v%5C%22%2C%5C%22invertAPKFilter%5C%22%3Afalse%2C%5C%22autoApkFilterByArch%5C%22%3Atrue%2C%5C%22appName%5C%22%3A%5C%22YouTube%5C%22%2C%5C%22appAuthor%5C%22%3A%5C%22%5C%22%2C%5C%22shizukuPretendToBeGooglePlay%5C%22%3Afalse%2C%5C%22allowInsecure%5C%22%3Afalse%2C%5C%22exemptFromBackgroundUpdates%5C%22%3Afalse%2C%5C%22skipUpdateNotifications%5C%22%3Afalse%2C%5C%22about%5C%22%3A%5C%22%5C%22%2C%5C%22refreshBeforeDownload%5C%22%3Afalse%2C%5C%22includeZips%5C%22%3Afalse%2C%5C%22zippedApkFilterRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22dontSortReleasesList%5C%22%3Afalse%2C%5C%22github-creds%5C%22%3A%5C%22%5C%22%7D%22%2C%22overrideSource%22%3A%22GitHub%22%7D
[yt-exp-morphe]: https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22app.morphe.android.youtube%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FRajveer-Mahida%2Fmorphe-autobuilder-v2%22%2C%22author%22%3A%22Rajveer-Mahida%22%2C%22name%22%3A%22YouTube%20Experimental%22%2C%22preferredApkIndex%22%3A0%2C%22additionalSettings%22%3A%22%7B%5C%22includePrereleases%5C%22%3Afalse%2C%5C%22fallbackToOlderReleases%5C%22%3Atrue%2C%5C%22filterReleaseTitlesByRegEx%5C%22%3A%5C%22%5EMorphe%20Patches%20v%5C%22%2C%5C%22filterReleaseNotesByRegEx%5C%22%3A%5C%22%5C%5C%5C%5C%7C%20YouTube%5C%5C%5C%5C%20Experimental%20%5C%5C%5C%5C%7C%5C%22%2C%5C%22verifyLatestTag%5C%22%3Afalse%2C%5C%22sortMethodChoice%5C%22%3A%5C%22date%5C%22%2C%5C%22useLatestAssetDateAsReleaseDate%5C%22%3Afalse%2C%5C%22releaseTitleAsVersion%5C%22%3Afalse%2C%5C%22trackOnly%5C%22%3Afalse%2C%5C%22versionExtractionRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22matchGroupToUse%5C%22%3A%5C%22%5C%22%2C%5C%22versionDetection%5C%22%3Afalse%2C%5C%22releaseDateAsVersion%5C%22%3Afalse%2C%5C%22useVersionCodeAsOSVersion%5C%22%3Afalse%2C%5C%22apkFilterRegEx%5C%22%3A%5C%22%5Eyoutube%5C%5C%5C%5C-experimental%5C%5C%5C%5C-morphe%5C%5C%5C%5C-v%5C%22%2C%5C%22invertAPKFilter%5C%22%3Afalse%2C%5C%22autoApkFilterByArch%5C%22%3Atrue%2C%5C%22appName%5C%22%3A%5C%22YouTube%20Experimental%5C%22%2C%5C%22appAuthor%5C%22%3A%5C%22%5C%22%2C%5C%22shizukuPretendToBeGooglePlay%5C%22%3Afalse%2C%5C%22allowInsecure%5C%22%3Afalse%2C%5C%22exemptFromBackgroundUpdates%5C%22%3Afalse%2C%5C%22skipUpdateNotifications%5C%22%3Afalse%2C%5C%22about%5C%22%3A%5C%22%5C%22%2C%5C%22refreshBeforeDownload%5C%22%3Afalse%2C%5C%22includeZips%5C%22%3Afalse%2C%5C%22zippedApkFilterRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22dontSortReleasesList%5C%22%3Afalse%2C%5C%22github-creds%5C%22%3A%5C%22%5C%22%7D%22%2C%22overrideSource%22%3A%22GitHub%22%7D
[music-morphe]: https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22app.morphe.android.apps.youtube.music%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FRajveer-Mahida%2Fmorphe-autobuilder-v2%22%2C%22author%22%3A%22Rajveer-Mahida%22%2C%22name%22%3A%22YouTube%20Music%22%2C%22preferredApkIndex%22%3A0%2C%22additionalSettings%22%3A%22%7B%5C%22includePrereleases%5C%22%3Afalse%2C%5C%22fallbackToOlderReleases%5C%22%3Atrue%2C%5C%22filterReleaseTitlesByRegEx%5C%22%3A%5C%22%5EMorphe%20Patches%20v%5C%22%2C%5C%22filterReleaseNotesByRegEx%5C%22%3A%5C%22%5C%5C%5C%5C%7C%20Music%20%5C%5C%5C%5C%7C%5C%22%2C%5C%22verifyLatestTag%5C%22%3Afalse%2C%5C%22sortMethodChoice%5C%22%3A%5C%22date%5C%22%2C%5C%22useLatestAssetDateAsReleaseDate%5C%22%3Afalse%2C%5C%22releaseTitleAsVersion%5C%22%3Afalse%2C%5C%22trackOnly%5C%22%3Afalse%2C%5C%22versionExtractionRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22matchGroupToUse%5C%22%3A%5C%22%5C%22%2C%5C%22versionDetection%5C%22%3Afalse%2C%5C%22releaseDateAsVersion%5C%22%3Afalse%2C%5C%22useVersionCodeAsOSVersion%5C%22%3Afalse%2C%5C%22apkFilterRegEx%5C%22%3A%5C%22%5Emusic%5C%5C%5C%5C-morphe%5C%5C%5C%5C-v%5C%22%2C%5C%22invertAPKFilter%5C%22%3Afalse%2C%5C%22autoApkFilterByArch%5C%22%3Atrue%2C%5C%22appName%5C%22%3A%5C%22YouTube%20Music%5C%22%2C%5C%22appAuthor%5C%22%3A%5C%22%5C%22%2C%5C%22shizukuPretendToBeGooglePlay%5C%22%3Afalse%2C%5C%22allowInsecure%5C%22%3Afalse%2C%5C%22exemptFromBackgroundUpdates%5C%22%3Afalse%2C%5C%22skipUpdateNotifications%5C%22%3Afalse%2C%5C%22about%5C%22%3A%5C%22%5C%22%2C%5C%22refreshBeforeDownload%5C%22%3Afalse%2C%5C%22includeZips%5C%22%3Afalse%2C%5C%22zippedApkFilterRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22dontSortReleasesList%5C%22%3Afalse%2C%5C%22github-creds%5C%22%3A%5C%22%5C%22%7D%22%2C%22overrideSource%22%3A%22GitHub%22%7D
[music-exp-morphe]: https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22app.morphe.android.apps.youtube.music%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FRajveer-Mahida%2Fmorphe-autobuilder-v2%22%2C%22author%22%3A%22Rajveer-Mahida%22%2C%22name%22%3A%22YouTube%20Music%20Experimental%22%2C%22preferredApkIndex%22%3A0%2C%22additionalSettings%22%3A%22%7B%5C%22includePrereleases%5C%22%3Afalse%2C%5C%22fallbackToOlderReleases%5C%22%3Atrue%2C%5C%22filterReleaseTitlesByRegEx%5C%22%3A%5C%22%5EMorphe%20Patches%20v%5C%22%2C%5C%22filterReleaseNotesByRegEx%5C%22%3A%5C%22%5C%5C%5C%5C%7C%20Music%5C%5C%5C%5C%20Experimental%20%5C%5C%5C%5C%7C%5C%22%2C%5C%22verifyLatestTag%5C%22%3Afalse%2C%5C%22sortMethodChoice%5C%22%3A%5C%22date%5C%22%2C%5C%22useLatestAssetDateAsReleaseDate%5C%22%3Afalse%2C%5C%22releaseTitleAsVersion%5C%22%3Afalse%2C%5C%22trackOnly%5C%22%3Afalse%2C%5C%22versionExtractionRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22matchGroupToUse%5C%22%3A%5C%22%5C%22%2C%5C%22versionDetection%5C%22%3Afalse%2C%5C%22releaseDateAsVersion%5C%22%3Afalse%2C%5C%22useVersionCodeAsOSVersion%5C%22%3Afalse%2C%5C%22apkFilterRegEx%5C%22%3A%5C%22%5Emusic%5C%5C%5C%5C-experimental%5C%5C%5C%5C-morphe%5C%5C%5C%5C-v%5C%22%2C%5C%22invertAPKFilter%5C%22%3Afalse%2C%5C%22autoApkFilterByArch%5C%22%3Atrue%2C%5C%22appName%5C%22%3A%5C%22YouTube%20Music%20Experimental%5C%22%2C%5C%22appAuthor%5C%22%3A%5C%22%5C%22%2C%5C%22shizukuPretendToBeGooglePlay%5C%22%3Afalse%2C%5C%22allowInsecure%5C%22%3Afalse%2C%5C%22exemptFromBackgroundUpdates%5C%22%3Afalse%2C%5C%22skipUpdateNotifications%5C%22%3Afalse%2C%5C%22about%5C%22%3A%5C%22%5C%22%2C%5C%22refreshBeforeDownload%5C%22%3Afalse%2C%5C%22includeZips%5C%22%3Afalse%2C%5C%22zippedApkFilterRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22dontSortReleasesList%5C%22%3Afalse%2C%5C%22github-creds%5C%22%3A%5C%22%5C%22%7D%22%2C%22overrideSource%22%3A%22GitHub%22%7D
[reddit-morphe]: https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22com.reddit.frontpage%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FRajveer-Mahida%2Fmorphe-autobuilder-v2%22%2C%22author%22%3A%22Rajveer-Mahida%22%2C%22name%22%3A%22Reddit%22%2C%22preferredApkIndex%22%3A0%2C%22additionalSettings%22%3A%22%7B%5C%22includePrereleases%5C%22%3Afalse%2C%5C%22fallbackToOlderReleases%5C%22%3Atrue%2C%5C%22filterReleaseTitlesByRegEx%5C%22%3A%5C%22%5EMorphe%20Patches%20v%5C%22%2C%5C%22filterReleaseNotesByRegEx%5C%22%3A%5C%22%5C%5C%5C%5C%7C%20Reddit%20%5C%5C%5C%5C%7C%5C%22%2C%5C%22verifyLatestTag%5C%22%3Afalse%2C%5C%22sortMethodChoice%5C%22%3A%5C%22date%5C%22%2C%5C%22useLatestAssetDateAsReleaseDate%5C%22%3Afalse%2C%5C%22releaseTitleAsVersion%5C%22%3Afalse%2C%5C%22trackOnly%5C%22%3Afalse%2C%5C%22versionExtractionRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22matchGroupToUse%5C%22%3A%5C%22%5C%22%2C%5C%22versionDetection%5C%22%3Afalse%2C%5C%22releaseDateAsVersion%5C%22%3Afalse%2C%5C%22useVersionCodeAsOSVersion%5C%22%3Afalse%2C%5C%22apkFilterRegEx%5C%22%3A%5C%22%5Ereddit%5C%5C%5C%5C-morphe%5C%5C%5C%5C-v%5C%22%2C%5C%22invertAPKFilter%5C%22%3Afalse%2C%5C%22autoApkFilterByArch%5C%22%3Atrue%2C%5C%22appName%5C%22%3A%5C%22Reddit%5C%22%2C%5C%22appAuthor%5C%22%3A%5C%22%5C%22%2C%5C%22shizukuPretendToBeGooglePlay%5C%22%3Afalse%2C%5C%22allowInsecure%5C%22%3Afalse%2C%5C%22exemptFromBackgroundUpdates%5C%22%3Afalse%2C%5C%22skipUpdateNotifications%5C%22%3Afalse%2C%5C%22about%5C%22%3A%5C%22%5C%22%2C%5C%22refreshBeforeDownload%5C%22%3Afalse%2C%5C%22includeZips%5C%22%3Afalse%2C%5C%22zippedApkFilterRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22dontSortReleasesList%5C%22%3Afalse%2C%5C%22github-creds%5C%22%3A%5C%22%5C%22%7D%22%2C%22overrideSource%22%3A%22GitHub%22%7D
[reddit-exp-morphe]: https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22com.reddit.frontpage%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FRajveer-Mahida%2Fmorphe-autobuilder-v2%22%2C%22author%22%3A%22Rajveer-Mahida%22%2C%22name%22%3A%22Reddit%20Experimental%22%2C%22preferredApkIndex%22%3A0%2C%22additionalSettings%22%3A%22%7B%5C%22includePrereleases%5C%22%3Afalse%2C%5C%22fallbackToOlderReleases%5C%22%3Atrue%2C%5C%22filterReleaseTitlesByRegEx%5C%22%3A%5C%22%5EMorphe%20Patches%20v%5C%22%2C%5C%22filterReleaseNotesByRegEx%5C%22%3A%5C%22%5C%5C%5C%5C%7C%20Reddit%5C%5C%5C%5C%20Experimental%20%5C%5C%5C%5C%7C%5C%22%2C%5C%22verifyLatestTag%5C%22%3Afalse%2C%5C%22sortMethodChoice%5C%22%3A%5C%22date%5C%22%2C%5C%22useLatestAssetDateAsReleaseDate%5C%22%3Afalse%2C%5C%22releaseTitleAsVersion%5C%22%3Afalse%2C%5C%22trackOnly%5C%22%3Afalse%2C%5C%22versionExtractionRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22matchGroupToUse%5C%22%3A%5C%22%5C%22%2C%5C%22versionDetection%5C%22%3Afalse%2C%5C%22releaseDateAsVersion%5C%22%3Afalse%2C%5C%22useVersionCodeAsOSVersion%5C%22%3Afalse%2C%5C%22apkFilterRegEx%5C%22%3A%5C%22%5Ereddit%5C%5C%5C%5C-experimental%5C%5C%5C%5C-morphe%5C%5C%5C%5C-v%5C%22%2C%5C%22invertAPKFilter%5C%22%3Afalse%2C%5C%22autoApkFilterByArch%5C%22%3Atrue%2C%5C%22appName%5C%22%3A%5C%22Reddit%20Experimental%5C%22%2C%5C%22appAuthor%5C%22%3A%5C%22%5C%22%2C%5C%22shizukuPretendToBeGooglePlay%5C%22%3Afalse%2C%5C%22allowInsecure%5C%22%3Afalse%2C%5C%22exemptFromBackgroundUpdates%5C%22%3Afalse%2C%5C%22skipUpdateNotifications%5C%22%3Afalse%2C%5C%22about%5C%22%3A%5C%22%5C%22%2C%5C%22refreshBeforeDownload%5C%22%3Afalse%2C%5C%22includeZips%5C%22%3Afalse%2C%5C%22zippedApkFilterRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22dontSortReleasesList%5C%22%3Afalse%2C%5C%22github-creds%5C%22%3A%5C%22%5C%22%7D%22%2C%22overrideSource%22%3A%22GitHub%22%7D
[x-piko]: https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22com.twitter.android%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FRajveer-Mahida%2Fmorphe-autobuilder-v2%22%2C%22author%22%3A%22Rajveer-Mahida%22%2C%22name%22%3A%22X%22%2C%22preferredApkIndex%22%3A0%2C%22additionalSettings%22%3A%22%7B%5C%22includePrereleases%5C%22%3Afalse%2C%5C%22fallbackToOlderReleases%5C%22%3Atrue%2C%5C%22filterReleaseTitlesByRegEx%5C%22%3A%5C%22%5EPiko%20Patches%20v%5C%22%2C%5C%22filterReleaseNotesByRegEx%5C%22%3A%5C%22%5C%5C%5C%5C%7C%20X%20%5C%5C%5C%5C%7C%5C%22%2C%5C%22verifyLatestTag%5C%22%3Afalse%2C%5C%22sortMethodChoice%5C%22%3A%5C%22date%5C%22%2C%5C%22useLatestAssetDateAsReleaseDate%5C%22%3Afalse%2C%5C%22releaseTitleAsVersion%5C%22%3Afalse%2C%5C%22trackOnly%5C%22%3Afalse%2C%5C%22versionExtractionRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22matchGroupToUse%5C%22%3A%5C%22%5C%22%2C%5C%22versionDetection%5C%22%3Afalse%2C%5C%22releaseDateAsVersion%5C%22%3Afalse%2C%5C%22useVersionCodeAsOSVersion%5C%22%3Afalse%2C%5C%22apkFilterRegEx%5C%22%3A%5C%22%5Ex%5C%5C%5C%5C-piko%5C%5C%5C%5C-v%5C%22%2C%5C%22invertAPKFilter%5C%22%3Afalse%2C%5C%22autoApkFilterByArch%5C%22%3Atrue%2C%5C%22appName%5C%22%3A%5C%22X%5C%22%2C%5C%22appAuthor%5C%22%3A%5C%22%5C%22%2C%5C%22shizukuPretendToBeGooglePlay%5C%22%3Afalse%2C%5C%22allowInsecure%5C%22%3Afalse%2C%5C%22exemptFromBackgroundUpdates%5C%22%3Afalse%2C%5C%22skipUpdateNotifications%5C%22%3Afalse%2C%5C%22about%5C%22%3A%5C%22%5C%22%2C%5C%22refreshBeforeDownload%5C%22%3Afalse%2C%5C%22includeZips%5C%22%3Afalse%2C%5C%22zippedApkFilterRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22dontSortReleasesList%5C%22%3Afalse%2C%5C%22github-creds%5C%22%3A%5C%22%5C%22%7D%22%2C%22overrideSource%22%3A%22GitHub%22%7D
[twitter-piko]: https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22com.twitter.android%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FRajveer-Mahida%2Fmorphe-autobuilder-v2%22%2C%22author%22%3A%22Rajveer-Mahida%22%2C%22name%22%3A%22Twitter%22%2C%22preferredApkIndex%22%3A0%2C%22additionalSettings%22%3A%22%7B%5C%22includePrereleases%5C%22%3Afalse%2C%5C%22fallbackToOlderReleases%5C%22%3Atrue%2C%5C%22filterReleaseTitlesByRegEx%5C%22%3A%5C%22%5EPiko%20Patches%20v%5C%22%2C%5C%22filterReleaseNotesByRegEx%5C%22%3A%5C%22%5C%5C%5C%5C%7C%20Twitter%20%5C%5C%5C%5C%7C%5C%22%2C%5C%22verifyLatestTag%5C%22%3Afalse%2C%5C%22sortMethodChoice%5C%22%3A%5C%22date%5C%22%2C%5C%22useLatestAssetDateAsReleaseDate%5C%22%3Afalse%2C%5C%22releaseTitleAsVersion%5C%22%3Afalse%2C%5C%22trackOnly%5C%22%3Afalse%2C%5C%22versionExtractionRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22matchGroupToUse%5C%22%3A%5C%22%5C%22%2C%5C%22versionDetection%5C%22%3Afalse%2C%5C%22releaseDateAsVersion%5C%22%3Afalse%2C%5C%22useVersionCodeAsOSVersion%5C%22%3Afalse%2C%5C%22apkFilterRegEx%5C%22%3A%5C%22%5Etwitter%5C%5C%5C%5C-piko%5C%5C%5C%5C-v%5C%22%2C%5C%22invertAPKFilter%5C%22%3Afalse%2C%5C%22autoApkFilterByArch%5C%22%3Atrue%2C%5C%22appName%5C%22%3A%5C%22Twitter%5C%22%2C%5C%22appAuthor%5C%22%3A%5C%22%5C%22%2C%5C%22shizukuPretendToBeGooglePlay%5C%22%3Afalse%2C%5C%22allowInsecure%5C%22%3Afalse%2C%5C%22exemptFromBackgroundUpdates%5C%22%3Afalse%2C%5C%22skipUpdateNotifications%5C%22%3Afalse%2C%5C%22about%5C%22%3A%5C%22%5C%22%2C%5C%22refreshBeforeDownload%5C%22%3Afalse%2C%5C%22includeZips%5C%22%3Afalse%2C%5C%22zippedApkFilterRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22dontSortReleasesList%5C%22%3Afalse%2C%5C%22github-creds%5C%22%3A%5C%22%5C%22%7D%22%2C%22overrideSource%22%3A%22GitHub%22%7D
[instagram-piko]: https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22com.instagram.android%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2FRajveer-Mahida%2Fmorphe-autobuilder-v2%22%2C%22author%22%3A%22Rajveer-Mahida%22%2C%22name%22%3A%22Instagram%22%2C%22preferredApkIndex%22%3A0%2C%22additionalSettings%22%3A%22%7B%5C%22includePrereleases%5C%22%3Afalse%2C%5C%22fallbackToOlderReleases%5C%22%3Atrue%2C%5C%22filterReleaseTitlesByRegEx%5C%22%3A%5C%22%5EPiko%20Patches%20v%5C%22%2C%5C%22filterReleaseNotesByRegEx%5C%22%3A%5C%22%5C%5C%5C%5C%7C%20Instagram%20%5C%5C%5C%5C%7C%5C%22%2C%5C%22verifyLatestTag%5C%22%3Afalse%2C%5C%22sortMethodChoice%5C%22%3A%5C%22date%5C%22%2C%5C%22useLatestAssetDateAsReleaseDate%5C%22%3Afalse%2C%5C%22releaseTitleAsVersion%5C%22%3Afalse%2C%5C%22trackOnly%5C%22%3Afalse%2C%5C%22versionExtractionRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22matchGroupToUse%5C%22%3A%5C%22%5C%22%2C%5C%22versionDetection%5C%22%3Afalse%2C%5C%22releaseDateAsVersion%5C%22%3Afalse%2C%5C%22useVersionCodeAsOSVersion%5C%22%3Afalse%2C%5C%22apkFilterRegEx%5C%22%3A%5C%22%5Einstagram%5C%5C%5C%5C-piko%5C%5C%5C%5C-v%5C%22%2C%5C%22invertAPKFilter%5C%22%3Afalse%2C%5C%22autoApkFilterByArch%5C%22%3Atrue%2C%5C%22appName%5C%22%3A%5C%22Instagram%5C%22%2C%5C%22appAuthor%5C%22%3A%5C%22%5C%22%2C%5C%22shizukuPretendToBeGooglePlay%5C%22%3Afalse%2C%5C%22allowInsecure%5C%22%3Afalse%2C%5C%22exemptFromBackgroundUpdates%5C%22%3Afalse%2C%5C%22skipUpdateNotifications%5C%22%3Afalse%2C%5C%22about%5C%22%3A%5C%22%5C%22%2C%5C%22refreshBeforeDownload%5C%22%3Afalse%2C%5C%22includeZips%5C%22%3Afalse%2C%5C%22zippedApkFilterRegEx%5C%22%3A%5C%22%5C%22%2C%5C%22dontSortReleasesList%5C%22%3Afalse%2C%5C%22github-creds%5C%22%3A%5C%22%5C%22%7D%22%2C%22overrideSource%22%3A%22GitHub%22%7D
