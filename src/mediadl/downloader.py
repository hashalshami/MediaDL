from __future__ import annotations

import asyncio
import inspect
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .config import DownloaderConfig
from .engines.ytdlp import YTDlpEngine
from .exceptions import DownloadError, UnsupportedURLError
from .formats.selector import select_format, sort_formats
from .models import DownloadResult, MediaInfo, ProgressCallback, ProgressEvent
from .utils import format_filesize

class Downloader:
    """Synchronous public MediaDL API."""

    def __init__(self, config: DownloaderConfig | None = None, **kwargs: Any) -> None:
        self.config = config or DownloaderConfig(**kwargs)
        self._engine = YTDlpEngine(self._base_options())

    def _base_options(self) -> dict[str, Any]:
        options: dict[str, Any] = {
            "quiet": self.config.quiet,
            "no_warnings": self.config.no_warnings,
            "noplaylist": self.config.noplaylist,
        }
        if self.config.proxy:
            options["proxy"] = self.config.proxy
        if self.config.cookies:
            options["cookiefile"] = self.config.cookies
        if self.config.ffmpeg_location:
            options["ffmpeg_location"] = self.config.ffmpeg_location
        return options

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise UnsupportedURLError(f"Invalid HTTP(S) URL: {url!r}")

    def inspect(self, url: str) -> MediaInfo:
        self._validate_url(url)
        return self._engine.inspect(url)

    def formats(self, url: str):
        return sort_formats(list(self.inspect(url).formats))

    def download(
        self,
        url: str,
        *,
        quality: str | int | None = None,
        output_dir: str | Path | None = None,
        filename_template: str | None = None,
        audio_only: bool = False,
        audio_format: str | None = None,
        max_filesize: int | str | None = None,
        on_progress: ProgressCallback | None = None,
        retries: int | None = None,
    ) -> DownloadResult:
        self._validate_url(url)
        out = Path(output_dir or self.config.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        quality_value = quality or self.config.quality
        size_limit = max_filesize if max_filesize is not None else self.config.max_filesize
        fmt = select_format(quality_value, audio_only=audio_only, max_filesize=size_limit, merge_format=self.config.merge_format)
        template = filename_template or self.config.filename_template
        template = str(out / template)
        attempts = self.config.retries if retries is None else retries
        last_error: Exception | None = None

        def hook(data: dict[str, Any]) -> None:
            if on_progress is None:
                return
            status = data.get("status", "unknown")
            downloaded = int(data.get("downloaded_bytes") or 0)
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            percent = downloaded / total * 100 if total else None
            event = ProgressEvent(status=status, downloaded=downloaded, total=total,
                                  percent=percent, speed=data.get("speed"), eta=data.get("eta"),
                                  filename=Path(data["filename"]) if data.get("filename") else None,
                                  message=data.get("info_dict", {}).get("title"))
            result = on_progress(event)
            if inspect.isawaitable(result):
                # Sync API deliberately does not own an event loop; callers should use AsyncDownloader.
                return

        options: dict[str, Any] = {
            "format": fmt,
            "outtmpl": template,
            "merge_output_format": self.config.merge_format,
            "progress_hooks": [hook],
            "retries": 0,
            "fragment_retries": 0,
            "noplaylist": True,
        }
        if audio_only:
            options["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": audio_format or "mp3"}]
        for attempt in range(attempts + 1):
            try:
                if on_progress:
                    on_progress(ProgressEvent(status="started", message=url))
                result = self._engine.download(url, options)
                if size_limit is not None:
                    limit = format_filesize(size_limit)
                    if limit and result.filesize > limit:
                        try:
                            result.path.unlink(missing_ok=True)
                        finally:
                            raise DownloadError(f"Downloaded file is {result.filesize} bytes; limit is {limit} bytes")
                if on_progress:
                    on_progress(ProgressEvent(status="finished", downloaded=result.filesize, total=result.filesize,
                                              percent=100.0, filename=result.path, message=result.title))
                return result
            except Exception as exc:
                last_error = exc
                if attempt >= attempts:
                    break
                time.sleep(self.config.retry_sleep * (2 ** attempt))
        assert last_error is not None
        raise last_error

    def close(self) -> None:
        return None

    def __enter__(self) -> "Downloader":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

class AsyncDownloader:
    """Async facade that runs the blocking extraction engine in a worker thread."""

    def __init__(self, config: DownloaderConfig | None = None, **kwargs: Any) -> None:
        self._sync = Downloader(config, **kwargs)

    async def inspect(self, url: str) -> MediaInfo:
        return await asyncio.to_thread(self._sync.inspect, url)

    async def formats(self, url: str):
        return await asyncio.to_thread(self._sync.formats, url)

    async def download(self, url: str, **kwargs: Any) -> DownloadResult:
        return await asyncio.to_thread(self._sync.download, url, **kwargs)

    async def close(self) -> None:
        self._sync.close()

    async def __aenter__(self) -> "AsyncDownloader":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
