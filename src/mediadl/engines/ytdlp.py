from __future__ import annotations

from pathlib import Path
from typing import Any

import yt_dlp

from ..exceptions import DownloadError, ExtractionError
from ..models import DownloadResult, Format, MediaInfo
from .base import ExtractionEngine


class YTDlpEngine(ExtractionEngine):
    def __init__(self, base_options: dict[str, Any] | None = None) -> None:
        self.base_options = dict(base_options or {})

    def _options(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        options = {"quiet": True, "no_warnings": True, **self.base_options}
        if extra:
            options.update(extra)
        return options

    @staticmethod
    def _format(item: dict[str, Any]) -> Format:
        return Format(
            id=str(item.get("format_id", "")),
            ext=item.get("ext"),
            resolution=item.get("resolution"),
            width=item.get("width"),
            height=item.get("height"),
            fps=item.get("fps"),
            filesize=item.get("filesize"),
            filesize_approx=item.get("filesize_approx"),
            tbr=item.get("tbr"),
            vcodec=item.get("vcodec"),
            acodec=item.get("acodec"),
            has_video=bool(item.get("vcodec") not in (None, "none")),
            has_audio=bool(item.get("acodec") not in (None, "none")),
            protocol=item.get("protocol"),
        )

    def inspect(self, url: str, *, playlist: bool = False) -> MediaInfo:
        opts = self._options(
            {"skip_download": True, "noplaylist": not playlist}
        )
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                data = ydl.extract_info(url, download=False)
        except Exception as exc:
            raise ExtractionError(str(exc)) from exc
        return self._to_info(data, url)

    def download(self, url: str, options: dict[str, Any]) -> DownloadResult:
        opts = self._options(options)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                data = ydl.extract_info(url, download=True)
                filename = Path(ydl.prepare_filename(data))
                if not filename.exists():
                    candidates = sorted(
                        filename.parent.glob(filename.stem + ".*"),
                        key=lambda p: p.stat().st_mtime,
                        reverse=True,
                    )
                    if candidates:
                        filename = candidates[0]
                if not filename.exists():
                    raise DownloadError(
                        "yt-dlp completed but the output file was not found"
                    )
        except DownloadError:
            raise
        except Exception as exc:
            raise DownloadError(str(exc)) from exc

        info = self._to_info(data, url)
        fmt = None
        if data.get("requested_formats"):
            fmt = self._format(data["requested_formats"][0])
        elif data.get("format_id"):
            fmt = self._format(data)

        return DownloadResult(
            filename,
            info.title,
            filename.suffix.lstrip("."),
            filename.stat().st_size,
            info.duration,
            fmt,
            info,
        )

    def _to_info(self, data: dict[str, Any], url: str) -> MediaInfo:
        formats = tuple(
            self._format(item)
            for item in data.get("formats", [])
            if item.get("format_id")
        )
        return MediaInfo(
            id=str(data.get("id", "")),
            title=str(data.get("title") or data.get("id") or "media"),
            webpage_url=str(data.get("webpage_url") or url),
            extractor=data.get("extractor_key") or data.get("extractor"),
            uploader=data.get("uploader") or data.get("channel"),
            duration=data.get("duration"),
            thumbnail=data.get("thumbnail"),
            description=data.get("description"),
            is_live=bool(data.get("is_live")),
            formats=formats,
            raw=data,
        )
