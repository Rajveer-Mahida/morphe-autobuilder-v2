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
# Added in the morphe-autobuilder-v2 fork: ABI matching shared by the
# Uptodown and APKPure scrapers.

import re

_KNOWN_ABIS: frozenset[str] = frozenset({"arm64-v8a", "armeabi-v7a", "armeabi", "x86", "x86_64"})
_UNIVERSAL_LABELS: frozenset[str] = frozenset({"", "universal", "noarch", "nodpi", "anydpi"})


def parse_abis(label: str) -> frozenset[str]:
    """Turn a store's architecture label into a set of ABIs.

    'arm64-v8a, armeabi-v7a' -> {arm64-v8a, armeabi-v7a}; 'universal' / '' -> empty set,
    which means the file carries no native code and runs on every ABI.
    """
    text = label.strip().lower()
    if text in _UNIVERSAL_LABELS:
        return frozenset()
    return frozenset(tok for tok in re.split(r"[\s,+/]+", text) if tok in _KNOWN_ABIS)


def abi_matches(abis: frozenset[str], arch: str) -> bool:
    """Whether a file with these ABIs satisfies the requested build arch.

    'all' must run on both ARM ABIs, so a single-ABI file is rejected rather than shipped
    under an '-all' name that crashes on half the devices.
    """
    if not abis:
        return True
    if arch == "all":
        return {"arm64-v8a", "armeabi-v7a"} <= abis
    return arch in abis
