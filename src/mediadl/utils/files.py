from __future__ import annotations

import re
from pathlib import Path

_UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_SIZE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([kmgtpe]?i?b)?\s*$", re.IGNORECASE)
_WINDOWS_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *{f"COM{i}" for i in range(1, 10)},
    *{f"LPT{i}" for i in range(1, 10)},
}

_DECIMAL_UNITS = {
    "kb": 1_000,
    "mb": 1_000_000,
    "gb": 1_000_000_000,
    "tb": 1_000_000_000_000,
    "pb": 1_000_000_000_000_000,
    "eb": 1_000_000_000_000_000_000,
}
_BINARY_UNITS = {
    "kib": 1024,
    "mib": 1024**2,
    "gib": 1024**3,
    "tib": 1024**4,
    "pib": 1024**5,
    "eib": 1024**6,
}


def format_filesize(value: int | float | str) -> int:
    """Convert a byte count or human-readable size into integer bytes."""
    if isinstance(value, bool):
        raise TypeError("filesize must be a number or size string")
    if isinstance(value, (int, float)):
        if value < 0:
            raise ValueError("filesize must be >= 0")
        return int(value)

    match = _SIZE.fullmatch(value)
    if not match:
        raise ValueError(f"Invalid filesize: {value!r}")

    number = float(match.group(1))
    unit = (match.group(2) or "b").lower()
    if unit == "b":
        multiplier = 1
    elif unit in _DECIMAL_UNITS:
        multiplier = _DECIMAL_UNITS[unit]
    elif unit in _BINARY_UNITS:
        multiplier = _BINARY_UNITS[unit]
    else:
        raise ValueError(f"Unsupported filesize unit: {unit!r}")
    return int(number * multiplier)


def sanitize_filename(name: str, replacement: str = "_") -> str:
    cleaned = _UNSAFE.sub(replacement, name)
    cleaned = cleaned.strip().rstrip(".")
    if not cleaned:
        return "media"
    if cleaned.upper() in _WINDOWS_RESERVED:
        cleaned = f"_{cleaned}"
    return cleaned


def ensure_suffix(path: Path, suffix: str) -> Path:
    if path.suffix.lower() == suffix.lower():
        return path
    return path.with_suffix(suffix)
