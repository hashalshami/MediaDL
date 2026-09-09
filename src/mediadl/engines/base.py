from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models import DownloadResult, MediaInfo


class ExtractionEngine(ABC):
    @abstractmethod
    def inspect(self, url: str, *, playlist: bool = False) -> MediaInfo: ...

    @abstractmethod
    def download(self, url: str, options: dict[str, Any]) -> DownloadResult: ...
