class MediaDLError(Exception):
    """Base exception for MediaDL."""


class UnsupportedURLError(MediaDLError):
    """Raised when no extraction engine can handle a URL."""


class ExtractionError(MediaDLError):
    """Raised when media metadata extraction fails."""


class DownloadError(MediaDLError):
    """Raised when a media download fails."""


class FFmpegNotFoundError(MediaDLError):
    """Raised when an operation requiring FFmpeg cannot find it."""
