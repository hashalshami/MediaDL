from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

ProgressCallback = Callable[["ProgressEvent"], Any]

@dataclass(frozen=True, slots=True)
class Format:
    id: str
    ext: str | None = None
    resolution: str | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    filesize: int | None = None
    filesize_approx: int | None = None
    tbr: float | None = None
    vcodec: str | None = None
    acodec: str | None = None
    has_video: bool = False
    has_audio: bool = False
    protocol: str | None = None

    @property
    def estimated_size(self) -> int | None:
        return self.filesize or self.filesize_approx

@dataclass(frozen=True, slots=True)
class MediaInfo:
    id: str
    title: str
    webpage_url: str
    extractor: str | None = None
    uploader: str | None = None
    duration: float | None = None
    thumbnail: str | None = None
    description: str | None = None
    is_live: bool = False
    formats: tuple[Format, ...] = field(default_factory=tuple)
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

@dataclass(frozen=True, slots=True)
class ProgressEvent:
    status: str
    downloaded: int = 0
    total: int | None = None
    percent: float | None = None
    speed: float | None = None
    eta: int | None = None
    filename: Path | None = None
    message: str | None = None

@dataclass(frozen=True, slots=True)
class DownloadResult:
    path: Path
    title: str
    extension: str
    filesize: int
    duration: float | None
    format: Format | None
    info: MediaInfo

@dataclass(frozen=True, slots=True)
class PlaylistResult:
    results: tuple[DownloadResult, ...]
    failed: tuple[str, ...] = field(default_factory=tuple)

    @property
    def total(self) -> int:
        return len(self.results) + len(self.failed)
