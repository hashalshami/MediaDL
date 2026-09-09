from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DownloaderConfig:
    output_dir: Path = Path("downloads")
    # yt-dlp output-template syntax is used intentionally; it keeps the full
    # power of its naming system.
    filename_template: str = "%(title)s [%(id)s].%(ext)s"
    quality: str = "best"
    merge_format: str = "mp4"
    retries: int = 3
    retry_sleep: float = 1.0
    max_filesize: int | None = None
    proxy: str | None = None
    cookies: str | None = None
    ffmpeg_location: str | None = None
    quiet: bool = True
    no_warnings: bool = True
    noplaylist: bool = True

    def __post_init__(self) -> None:
        if self.retries < 0:
            raise ValueError("retries must be >= 0")
        if self.retry_sleep < 0:
            raise ValueError("retry_sleep must be >= 0")
        if self.max_filesize is not None and self.max_filesize <= 0:
            raise ValueError("max_filesize must be > 0")
