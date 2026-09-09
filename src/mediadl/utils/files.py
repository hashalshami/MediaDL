from __future__ import annotations

import re
from pathlib import Path

_UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *{f"COM{i}" for i in range(1, 10)}, *{f"LPT{i}" for i in range(1, 10)}}


def sanitize_filename(name: str, replacement: str = "_") -> str:
    name = _UNSAFE.sub(replacement, name).strip().rstrip(".")
    if not name:
        return "media"
    stem = Path(name).stem.upper()
    if stem in _WINDOWS_RESERVED:
        name = f"_{name}"
    return name[:240]


def format_filesize(value: int | str | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([kmgt]?i?b)?\s*", value, re.I)
    if not match:
        raise ValueError(f"Invalid file size: {value!r}")
    number = float(match.group(1))
    unit = (match.group(2) or "b").lower()
    multipliers = {"b": 1, "kb": 1000, "mb": 1000**2, "gb": 1000**3, "tb": 1000**4,
                   "kib": 1024, "mib": 1024**2, "gib": 1024**3, "tib": 1024**4}
    return int(number * multipliers[unit])
