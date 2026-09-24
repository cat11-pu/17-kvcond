import json
import threading
import unittest
import urllib.error
import urllib.request

from kvstore import KV
from server import serve


class TestKV(unittest.TestCase):
    def test_put_and_get(self):
        store = KV()
        store.put("a", "1")
        self.assertEqual(store.get("a"), "1")

    def test_version_advances(self):
        store = KV()
        first = store.put("a", "1")
        second = store.put("a", "2")
        self.assertGreater(second, first)

    def test_missing_key_version_zero(self):
        self.assertEqual(KV().version("ghost"), 0)

    def test_http_roundtrip(self):
        server = serve(0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = "http://127.0.0.1:%d" % server.server_port
        request = urllib.request.Request(base + "/kv/a", data=b'{"value": "1"}', method="PUT")
        with urllib.request.urlopen(request, timeout=5) as response:
            self.assertEqual(json.loads(response.read())["version"], 1)
        with urllib.request.urlopen(base + "/kv/a", timeout=5) as response:
            self.assertEqual(json.loads(response.read())["value"], "1")
        server.shutdown()

    def test_missing_key_404(self):
        server = serve(0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = "http://127.0.0.1:%d" % server.server_port
        with self.assertRaises(urllib.error.HTTPError):
            urllib.request.urlopen(base + "/kv/ghost", timeout=5)
        server.shutdown()


if __name__ == "__main__":
    unittest.main()
