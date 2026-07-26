"""Regression test for the VariantH Neo4j publish path (BL-2609 follow-up).

The bug: _run_variant_h_diagnostic opened its own driver via self.neo4j_uri /
self.neo4j_user / self.neo4j_password — attributes never assigned in
EFCResearchDaemon.__init__ — so the publish step always died with
AttributeError (swallowed by the fail-soft except; VariantHResult nodes were
silently never written). The fix reuses ResearchPublisher._get_driver().

Mock-based: no Neo4j and no MCMC run required. Note: run_variant_h_diagnostic
is not yet implemented in research_mcmc (science stub pending); the patches
below use create=True to stub the contract the daemon imports lazily.
"""

import logging
import unittest
from unittest import mock

from efc_inference.runs.research_daemon import EFCResearchDaemon

FAKE_RESULT = {
    "verdict": "PASS",
    "S_bar_0_mean": 1.0,
    "S_bar_0_std": 0.1,
    "S_bar_0_sigma": 10.0,
    "beta_0_mean": 0.5,
    "beta_0_std": 0.05,
    "dll_growth": 1.2,
    "dll_total": 1.3,
    "daic": -2.0,
    "dbic": -1.0,
}


class _FakeSession:
    def __init__(self, calls):
        self._calls = calls

    def run(self, cypher, params):
        self._calls.append((cypher, params))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _FakeDriver:
    def __init__(self):
        self.run_calls = []
        self.closed = False

    def session(self):
        return _FakeSession(self.run_calls)

    def close(self):
        self.closed = True


def _bare_daemon(driver):
    """EFCResearchDaemon without running __init__ (skips policy/cosmology I/O).

    Deliberately does NOT set neo4j_uri/user/password — the publish path must
    not depend on them.
    """
    daemon = EFCResearchDaemon.__new__(EFCResearchDaemon)
    daemon.publisher = mock.Mock()
    daemon.publisher._get_driver.return_value = driver
    return daemon


class VariantHPublishTest(unittest.TestCase):
    def test_publishes_via_shared_driver_without_neo4j_attrs(self):
        driver = _FakeDriver()
        daemon = _bare_daemon(driver)
        with mock.patch(
            "efc_inference.runs.research_mcmc.run_variant_h_diagnostic",
            create=True,
            return_value=FAKE_RESULT,
        ):
            with self.assertLogs(level=logging.INFO) as captured:
                daemon._run_variant_h_diagnostic("test_cycle_001")

        self.assertEqual(len(driver.run_calls), 1)
        cypher, params = driver.run_calls[0]
        self.assertIn("VariantHResult", cypher)
        self.assertEqual(params["cycle_id"], "test_cycle_001")
        self.assertEqual(params["verdict"], "PASS")
        # Shared driver is owned by ResearchPublisher — must not be closed here.
        self.assertFalse(driver.closed)
        self.assertFalse(
            any("Neo4j publish failed" in line for line in captured.output),
            f"publish path errored: {captured.output}",
        )

    def test_fail_soft_when_driver_unavailable(self):
        daemon = _bare_daemon(None)
        with mock.patch(
            "efc_inference.runs.research_mcmc.run_variant_h_diagnostic",
            create=True,
            return_value=FAKE_RESULT,
        ):
            with self.assertLogs(level=logging.WARNING) as captured:
                daemon._run_variant_h_diagnostic("test_cycle_002")

        self.assertTrue(
            any("Neo4j publish failed" in line for line in captured.output)
        )


if __name__ == "__main__":
    unittest.main()
