from mediadl.formats.selector import select_format


def test_quality():
    assert "height<=720" in select_format("720p")
    assert select_format("best") == "bestvideo+bestaudio/best[ext=mp4]/best"
    assert select_format("best", audio_only=True) == "bestaudio/best"
