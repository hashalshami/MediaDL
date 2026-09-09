# MediaDL

Professional media downloading for Python, powered by yt-dlp.

MediaDL provides a clean API for inspecting and downloading supported public media URLs without coupling application code to yt-dlp's internal dictionaries. It includes format selection, size limits, progress events, retries, audio extraction, filename sanitization, cookies, proxy configuration, async and sync APIs, and a CLI.

> Use MediaDL only for content you are authorized to download and in accordance with the source service's terms and applicable law.

## Requirements

- Python 3.10+
- `ffmpeg` and `ffprobe` for merging separate audio/video streams and post-processing
- A JavaScript runtime may be required by yt-dlp for some extractors

## Install

```bash
pip install mediadl-engine
```

Development install:

```bash
pip install -e ".[dev]"
```

## Python API

```python
from mediadl import Downloader

with Downloader() as downloader:
    info = downloader.inspect("https://example.com/video")
    print(info.title, info.duration)
    result = downloader.download(
        "https://example.com/video",
        quality="720p",
        output_dir="downloads",
    )
    print(result.path)
```

Async applications can use the same engine without blocking the event loop:

```python
import asyncio
from mediadl import AsyncDownloader

async def main():
    async with AsyncDownloader() as downloader:
        info = await downloader.inspect(url)
        result = await downloader.download(url, quality="720p")
        print(result.path)

asyncio.run(main())
```

### Progress

```python
from mediadl import Downloader, ProgressEvent

def on_progress(event: ProgressEvent) -> None:
    if event.percent is not None:
        print(f"{event.percent:.1f}%", event.speed, event.eta)

Downloader().download(url, on_progress=on_progress)
```

### Audio

```python
Downloader().download(
    url,
    audio_only=True,
    audio_format="mp3",
)
```

### Size-aware quality

```python
Downloader().download(
    url,
    quality="720p",
    max_filesize="150MB",
)
```

### Cookies and proxy

```python
Downloader(
    cookies="cookies.txt",
    proxy="socks5://127.0.0.1:1080",
)
```

## CLI

```bash
mediadl info "URL"
mediadl formats "URL"
mediadl download "URL" --quality 720p
mediadl download "URL" --audio --audio-format mp3
mediadl download "URL" --max-filesize 150MB
```

## Architecture

MediaDL deliberately separates orchestration, extraction, models, format selection, storage and post-processing. yt-dlp is an implementation detail behind the extraction engine, so application code depends on stable MediaDL models instead of yt-dlp's raw result dictionaries.

## License

MIT. See `LICENSE`.
