import unittest
from unittest.mock import patch

import json

from typer.testing import CliRunner

from dssldrf_cli.main import app


class _FakeClient:
    def __init__(self, items):
        self._items = items
        self.last_params = None

    def get(self, path, params=None):
        self.last_params = params or {}
        protocols = self.last_params.get("protocols", "")
        if not protocols:
            return self._items

        allowed = {value.strip().upper() for value in protocols.split(",") if value.strip()}
        return [
            item for item in self._items if str(item.get("protocol", "")).upper() in allowed
        ]


class ReqCommandTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.requests = [
            {
                "_id": "dns-1",
                "time": 1774749930,
                "protocol": "DNS",
                "clientip": "66.185.115.249",
                "zone": "m.dssldrf.net",
                "request": {"query": "one.example", "type": "A"},
                "response": {},
            },
            {
                "_id": "dns-2",
                "time": 1774749930,
                "protocol": "DNS",
                "clientip": "66.185.115.249",
                "zone": "m.dssldrf.net",
                "request": {"query": "two.example", "type": "A"},
                "response": {},
            },
            {
                "_id": "http-1",
                "time": 1774749930,
                "protocol": "HTTP",
                "clientip": "172.56.106.25",
                "zone": "m.dssldrf.net",
                "request": {"method": "GET", "path": "/probe"},
                "response": {"status": 200},
            },
            {
                "_id": "smtp-1",
                "time": 1774749930,
                "protocol": "SMTP",
                "clientip": "203.0.113.10",
                "zone": "m.dssldrf.net",
                "request": {},
                "response": {},
            },
        ]
        self.fake_client = _FakeClient(self.requests)

    def _invoke(self, args):
        with patch("dssldrf_cli.main._config_exists", return_value=True), patch(
            "dssldrf_cli.main.load_config"
        ) as load_config, patch("dssldrf_cli.main._api_client") as api_client:
            load_config.return_value.domain = "dssldrf.net"
            api_client.return_value = self.fake_client
            return self.runner.invoke(app, args)

    def test_timestamp_selector_shows_all_matches_in_text_output(self):
        result = self._invoke(["req", "m", "1774749930"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.count("id: 1774749930"), 4)
        self.assertIn("protocol: dns", result.output)
        self.assertIn("protocol: http", result.output)
        self.assertIn("protocol: smtp", result.output)

    def test_full_request_details_use_lowercase_labels(self):
        result = self._invoke(["req", "m", "--id", "http-1"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("request:", result.output)
        self.assertIn("  method: GET", result.output)
        self.assertIn("  path: /probe", result.output)
        self.assertIn("response:", result.output)
        self.assertIn("  status: 200", result.output)
        self.assertNotIn("REQUEST:", result.output)
        self.assertNotIn("RESPONSE:", result.output)

    def test_timestamp_selector_json_output_is_always_array(self):
        result = self._invoke(["req", "m", "--id", "1774749930", "--json"])

        self.assertEqual(result.exit_code, 0)
        payload = json.loads(result.output)
        self.assertIsInstance(payload, list)
        self.assertEqual(len(payload), 4)
        self.assertEqual(payload[2]["protocol"], "HTTP")

    def test_request_id_json_output_is_single_item_array(self):
        result = self._invoke(["req", "m", "--id", "http-1", "--json"])

        self.assertEqual(result.exit_code, 0)
        payload = json.loads(result.output)
        self.assertIsInstance(payload, list)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["_id"], "http-1")

    def test_http_filter_omits_other_protocols(self):
        result = self._invoke(["req", "m", "1774749930", "--http"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("protocol: http", result.output)
        self.assertNotIn("protocol: dns", result.output)
        self.assertNotIn("protocol: smtp", result.output)
        self.assertEqual(self.fake_client.last_params.get("protocols"), "HTTP")

    def test_http_and_dns_filters_limit_to_supported_shortcuts(self):
        result = self._invoke(["req", "m", "1774749930", "--http", "--dns"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("protocol: http", result.output)
        self.assertIn("protocol: dns", result.output)
        self.assertNotIn("protocol: smtp", result.output)
        self.assertEqual(self.fake_client.last_params.get("protocols"), "HTTP,DNS")


if __name__ == "__main__":
    unittest.main()