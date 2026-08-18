import tempfile
import unittest
from pathlib import Path

from context import BSE


class FakeResponse:
    """Minimal stand-in for a streamed requests.Response."""

    def __init__(self, status_code=200, reason="OK", chunks=(b"payload",)):
        self.status_code = status_code
        self.reason = reason
        self._chunks = chunks

    @property
    def ok(self):
        return self.status_code < 400

    def iter_content(self, chunk_size=None):
        yield from self._chunks

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


class Test_Download(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self._tmp.name)
        self.bse = BSE(download_folder=self.folder)
        # __download is name-mangled; bind it once for readability.
        self.download = self.bse._BSE__download

    def tearDown(self):
        self.bse.exit()
        self._tmp.cleanup()

    def _stub(self, response):
        self.bse.session.get = lambda *args, **kwargs: response

    def test_successful_download_writes_the_file(self):
        self._stub(FakeResponse(200, chunks=(b"col1,col2\n", b"1,2\n")))

        path = self.download("https://example.com/report.csv", self.folder)

        self.assertTrue(path.exists())
        self.assertEqual(path.read_bytes(), b"col1,col2\n1,2\n")

    def test_404_raises_runtime_error(self):
        self._stub(FakeResponse(404, "Not Found"))

        with self.assertRaises(RuntimeError):
            self.download("https://example.com/report.csv", self.folder)

    def test_server_error_body_is_not_written_as_a_report(self):
        # A 500 returns an HTML error page. Writing it to disk produces a
        # file that exists, passes the caller's exists() check, and is
        # then parsed as if it were a valid CSV report.
        self._stub(FakeResponse(500, "Internal Server Error", (b"<html>error</html>",)))

        with self.assertRaises(RuntimeError):
            self.download("https://example.com/report.csv", self.folder)

        self.assertEqual(list(self.folder.iterdir()), [])

    def test_forbidden_is_not_written_as_a_report(self):
        self._stub(FakeResponse(403, "Forbidden", (b"<html>denied</html>",)))

        with self.assertRaises(RuntimeError):
            self.download("https://example.com/report.csv", self.folder)

        self.assertEqual(list(self.folder.iterdir()), [])

    def test_partial_write_leaves_no_truncated_file(self):
        def explode(chunk_size=None):
            yield b"first chunk"
            raise ConnectionError("connection dropped mid-stream")

        response = FakeResponse(200)
        response.iter_content = explode
        self._stub(response)

        with self.assertRaises(ConnectionError):
            self.download("https://example.com/report.csv", self.folder)

        self.assertEqual(list(self.folder.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
