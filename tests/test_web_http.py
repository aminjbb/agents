import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from fagent.web_http import Server
from fagent.web_jobs import Jobs
from test_web_jobs import ConnectedAdapter


class WebHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "index.html").write_text("<main>Control room</main>")
        self.jobs = Jobs(self.root / "runs", lambda **_: ConnectedAdapter())
        self.addCleanup(self.jobs.close)
        self.server = Server(("127.0.0.1", 0), self.jobs, self.root)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def call(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            connection.request(method, path, body, headers or {})
            response = connection.getresponse()
            return response.status, response.read(), dict(response.getheaders())
        finally:
            connection.close()

    def test_real_registry_and_built_static(self):
        status, body, headers = self.call("GET", "/api/bootstrap")
        self.assertEqual(status, 200)
        result = json.loads(body)
        self.assertEqual(len(result["agents"]), 6)
        self.assertFalse(result["connection"]["configured"])
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertIn(b"Control room", self.call("GET", "/")[1])

    def test_mutation_requires_header_and_safe_origin(self):
        body = json.dumps({"api_key": "secret"})
        self.assertEqual(self.call("POST", "/api/connection", body)[0], 400)
        headers = {"X-FAgent-Client": "web", "Origin": "https://attacker.invalid"}
        self.assertEqual(self.call("POST", "/api/connection", body, headers)[0], 400)
        headers["Origin"] = f"http://127.0.0.1:{self.server.server_port}"
        status, result, _ = self.call("POST", "/api/connection", body, headers)
        self.assertEqual(status, 200)
        self.assertNotIn(b"secret", result)
        self.assertTrue(json.loads(result)["configured"])

    def test_host_traversal_body_shape_and_size_checks(self):
        self.assertEqual(self.call("GET", "/api/bootstrap", headers={"Host": "evil.invalid"})[0], 400)
        self.assertEqual(self.call("GET", "/%2e%2e/private.txt")[0], 400)
        headers = {"X-FAgent-Client": "web"}
        self.assertEqual(self.call("POST", "/api/connection", "[]", headers)[0], 400)
        self.assertEqual(self.call("POST", "/api/connection", "x" * 65537, headers)[0], 400)
