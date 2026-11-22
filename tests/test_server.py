import http.client
import socketserver
import threading
import unittest

from server import BotRequestHandler


class BotServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = socketserver.TCPServer(("127.0.0.1", 0), BotRequestHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thread.start()
        cls.port = cls.httpd.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.server_thread.join()

    def request(self, method, path, headers=None, body=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        result = (response.status, response.headers, response.read())
        connection.close()
        return result

    def test_dashboard_root_serves_static_entry_page(self):
        status, _, body = self.request("GET", "/")

        self.assertEqual(status, 200)
        self.assertIn("Interface no Vercel", body.decode("utf-8"))

    def test_vercel_origin_can_complete_private_network_preflight(self):
        origin = "https://src-amber-tau.vercel.app"
        status, headers, _ = self.request(
            "OPTIONS",
            "/api/simular-mensagens",
            {
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Private-Network": "true",
            },
        )

        self.assertEqual(status, 204)
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), origin)
        self.assertEqual(headers.get("Access-Control-Allow-Private-Network"), "true")

    def test_post_from_untrusted_origin_is_rejected(self):
        status, _, _ = self.request(
            "POST",
            "/api/executar-desktop",
            {"Origin": "https://untrusted.example"},
            body=b"",
        )

        self.assertEqual(status, 403)


if __name__ == "__main__":
    unittest.main()
