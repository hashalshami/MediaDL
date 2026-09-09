import mediadl


def test_public_api() -> None:
    assert mediadl.__version__ == "0.1.0"
    assert mediadl.Downloader is not None
    assert mediadl.AsyncDownloader is not None
