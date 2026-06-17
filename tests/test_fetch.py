import pytest

from ai_automation_kit.core.fetch import FetchPolicy, fetch_uri


def test_fetch_uri_reads_file_uri(tmp_path):
    source = tmp_path / "source.html"
    source.write_text("<html><body>safe</body></html>")

    fetched = fetch_uri(source.as_uri(), FetchPolicy())

    assert fetched.uri == source.as_uri()
    assert "safe" in fetched.content


@pytest.mark.parametrize(
    "uri",
    [
        "http://localhost/private",
        "http://127.0.0.1/private",
        "http://169.254.169.254/latest/meta-data",
        "http://10.0.0.1/internal",
        "http://192.168.1.2/internal",
    ],
)
def test_fetch_uri_rejects_private_network_targets(uri):
    with pytest.raises(ValueError, match="private network"):
        fetch_uri(uri, FetchPolicy())
