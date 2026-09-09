from __future__ import annotations

from ..models import Format
from ..utils import format_filesize


def select_format(
    quality: str | int,
    *,
    audio_only: bool = False,
    max_filesize: int | str | None = None,
    merge_format: str = "mp4",
) -> str:
    if audio_only:
        return "bestaudio/best"
    if isinstance(quality, int) or (
        isinstance(quality, str) and quality.isdigit()
    ):
        quality = f"{int(quality)}p"
    quality = quality.lower().strip()
    if quality in {"best", "bestvideo"}:
        expression = f"bestvideo+bestaudio/best[ext={merge_format}]/best"
    elif quality == "worst":
        expression = "worstvideo+worstaudio/worst"
    elif quality.endswith("p") and quality[:-1].isdigit():
        height = int(quality[:-1])
        expression = (
            f"bestvideo[height<={height}]+bestaudio/"
            f"best[height<={height}]/best"
        )
    else:
        raise ValueError(f"Unsupported quality preset: {quality!r}")

    if max_filesize is not None:
        size = format_filesize(max_filesize)
        # This is a pre-download hint. Final merged size is still validated by MediaDL.
        if size:
            expression = expression.replace(
                "bestvideo", f"bestvideo[filesize<{size}]"
            )
    return expression


def sort_formats(formats: list[Format]) -> list[Format]:
    return sorted(
        formats,
        key=lambda f: (
            f.height or 0,
            f.tbr or 0,
            f.estimated_size or 0,
        ),
        reverse=True,
    )
