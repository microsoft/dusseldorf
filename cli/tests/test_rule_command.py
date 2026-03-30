import json
import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from dssldrf_cli.main import app


class _FakeRuleClient:
    def __init__(self, rules_by_zone):
        self.rules_by_zone = rules_by_zone

    def list_all_rules(self):
        result = []
        for rules in self.rules_by_zone.values():
            result.extend(rules)
        return result

    def list_rules(self, zone):
        return list(self.rules_by_zone.get(zone, []))


class RuleCommandTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.rules_by_zone = {
            "a.dssldrf.net": [
                {
                    "zone": "a.dssldrf.net",
                    "name": "allow_home",
                    "networkprotocol": "HTTP",
                    "priority": 20,
                    "ruleid": "rule-http-20",
                    "rulecomponents": [{}, {}],
                },
                {
                    "zone": "a.dssldrf.net",
                    "name": "block_dns",
                    "networkprotocol": "DNS",
                    "priority": 10,
                    "ruleid": "rule-dns-10",
                    "rulecomponents": [{}],
                },
            ],
            "b.dssldrf.net": [
                {
                    "zone": "b.dssldrf.net",
                    "name": "deny_post",
                    "networkprotocol": "HTTP",
                    "priority": 5,
                    "ruleid": "rule-http-5",
                    "rulecomponents": [{}, {}, {}],
                }
            ],
        }
        self.fake_client = _FakeRuleClient(self.rules_by_zone)

    def _invoke(self, args):
        with patch("dssldrf_cli.main._config_exists", return_value=True), patch(
            "dssldrf_cli.main.load_config"
        ) as load_config, patch("dssldrf_cli.main._api_client", return_value=self.fake_client):
            load_config.return_value.domain = "dssldrf.net"
            return self.runner.invoke(app, args)

    def test_rule_without_zone_lists_all_accessible_rules_grouped_by_zone(self):
        result = self._invoke(["rule"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("zone: a.dssldrf.net", result.output)
        self.assertIn("zone: b.dssldrf.net", result.output)
        self.assertIn("  [dns] priority 10 block_dns (rule-dns-10, 1 components)", result.output)
        self.assertIn("  [http] priority 20 allow_home (rule-http-20, 2 components)", result.output)
        self.assertIn("  [http] priority 5 deny_post (rule-http-5, 3 components)", result.output)

    def test_rule_with_zone_lists_only_that_zone(self):
        result = self._invoke(["rule", "a"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("zone: a.dssldrf.net", result.output)
        self.assertNotIn("zone: b.dssldrf.net", result.output)
        self.assertIn("block_dns", result.output)
        self.assertIn("allow_home", result.output)

    def test_rule_with_zone_supports_json_output(self):
        result = self._invoke(["rule", "--json", "a"])

        self.assertEqual(result.exit_code, 0)
        payload = json.loads(result.output)
        self.assertEqual(len(payload), 2)
        self.assertEqual(payload[0]["zone"], "a.dssldrf.net")

    def test_rule_subcommands_still_work(self):
        result = self._invoke(["rule", "list-actions"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Supported predicates:", result.output)


if __name__ == "__main__":
    unittest.main()