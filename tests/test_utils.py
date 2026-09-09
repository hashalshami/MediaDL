import pytest

from mediadl.utils.files import format_filesize, sanitize_filename


def test_sizes() -> None:
    assert format_filesize("150MB") == 150_000_000
    assert format_filesize("1MiB") == 1_048_576
    assert format_filesize("2.5 GB") == 2_500_000_000
    assert format_filesize(1024) == 1024


def test_invalid_size() -> None:
    with pytest.raises(ValueError):
        format_filesize("10XB")


def test_filename() -> None:
    assert sanitize_filename("a:/bad*name?.mp4") == "a__bad_name_.mp4"
    assert sanitize_filename("CON") == "_CON"
    assert sanitize_filename("...") == "media"
