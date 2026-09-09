from mediadl.utils.files import format_filesize, sanitize_filename


def test_sizes():
    assert format_filesize("150MB") == 150_000_000
    assert format_filesize("1MiB") == 1_048_576


def test_filename():
    assert sanitize_filename('a:/bad*name?.mp4') == "a__bad_name_.mp4"
    assert sanitize_filename("CON") == "_CON"
