from __future__ import annotations

import argparse
import sys

from . import __version__
from .downloader import Downloader


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mediadl", description="Download supported media with MediaDL")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("info", "formats"):
        cmd = sub.add_parser(name)
        cmd.add_argument("url")

    cmd = sub.add_parser("download")
    cmd.add_argument("url")
    cmd.add_argument("--quality", default="best")
    cmd.add_argument("--output", default="downloads")
    cmd.add_argument("--audio", action="store_true")
    cmd.add_argument("--audio-format", default=None)
    cmd.add_argument("--max-filesize", default=None)
    cmd.add_argument("--proxy", default=None)
    cmd.add_argument("--cookies", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    downloader = Downloader(proxy=getattr(args, "proxy", None), cookies=getattr(args, "cookies", None))
    try:
        if args.command == "info":
            info = downloader.inspect(args.url)
            print(f"Title: {info.title}")
            print(f"ID: {info.id}")
            print(f"Extractor: {info.extractor}")
            print(f"Uploader: {info.uploader or '-'}")
            print(f"Duration: {info.duration or '-'}")
            print(f"Formats: {len(info.formats)}")
            return 0
        if args.command == "formats":
            for item in downloader.formats(args.url):
                size = item.estimated_size or "?"
                print(f"{item.id:>8} {item.ext or '-':>5} {item.resolution or '-':>12} {size!s:>12} {item.vcodec or '-'} / {item.acodec or '-'}")
            return 0

        def progress(event):
            if event.percent is not None:
                print(f"\r{event.status}: {event.percent:6.2f}%", end="", flush=True)
            elif event.status == "finished":
                print()

        result = downloader.download(
            args.url, quality=args.quality, output_dir=args.output, audio_only=args.audio,
            audio_format=args.audio_format, max_filesize=args.max_filesize, on_progress=progress,
        )
        print(f"Saved: {result.path}")
        return 0
    except Exception as exc:
        print(f"MediaDL error: {exc}", file=sys.stderr)
        return 1
    finally:
        downloader.close()
