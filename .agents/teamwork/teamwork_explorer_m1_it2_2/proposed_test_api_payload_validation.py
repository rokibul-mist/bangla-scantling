"""
Unit & Integration Test Suite for API Payload Validation and State Protection.
Tests defensive guards in endpoints_state, endpoints_calculation, state_service,
and state_repository against non-dict payloads.
"""

import os
import sys
import unittest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import Request
from app.api.v1.endpoints_state import save_state
from app.api.v1.endpoints_calculation import calculate_state
from app.services.state_service import StateService
from app.repositories.state_repository import StateRepository
from app.services.calculation_service import CalculationService


class TestStatePayloadValidation(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock(spec=StateRepository)
        self.mock_repo.get_raw_data.return_value = {
            "dashboard_inputs": {"loa": 76.21, "lbp": 69.85, "breadth": 13.41, "depth": 5.18, "draft": 4.0, "frame_spacing": 550},
            "stiffener_custom_dims": {},
            "empirical_tables": [],
            "application_form_pages": []
        }
        self.state_service = StateService(self.mock_repo)

    def test_save_state_non_dict_rejected_with_400(self):
        """Ensure save_state rejects list, string, int, and None payloads with HTTP 400."""
        invalid_payloads = [
            [],
            [1, 2, 3],
            "string_payload",
            123,
            True,
            None
        ]
        for payload in invalid_payloads:
            req = MagicMock(spec=Request)
            req.json = AsyncMock(return_value=payload)
            resp = asyncio.run(save_state(req, self.state_service))
            self.assertEqual(
                resp.status_code, 400,
                f"Expected status 400 for payload {payload!r}, got {resp.status_code}"
            )
            data = json.loads(resp.body.decode("utf-8"))
            self.assertEqual(data.get("status"), "error")
            self.assertFalse(self.mock_repo.save_state.called, "Repository save_state must not be called on invalid payload")

    def test_save_state_valid_dict_accepted_with_200(self):
        """Ensure save_state accepts valid dictionary payloads with HTTP 200."""
        self.mock_repo.save_state.return_value = True
        req = MagicMock(spec=Request)
        req.json = AsyncMock(return_value={"dashboard_inputs": {"vessel_name": "Test Ship"}})
        resp = asyncio.run(save_state(req, self.state_service))
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.body.decode("utf-8"))
        self.assertEqual(data.get("status"), "ok")

    def test_calculate_non_dict_rejected_with_400(self):
        """Ensure calculate rejects list, string, int, and None payloads with HTTP 400."""
        calc_service = CalculationService()
        invalid_payloads = [
            [],
            [1, 2, 3],
            "string_payload",
            123,
            True,
            None
        ]
        for payload in invalid_payloads:
            req = MagicMock(spec=Request)
            req.json = AsyncMock(return_value=payload)
            resp = asyncio.run(calculate_state(req, calc_service))
            self.assertEqual(
                resp.status_code, 400,
                f"Expected status 400 for calculate with payload {payload!r}, got {resp.status_code}"
            )
            data = json.loads(resp.body.decode("utf-8"))
            self.assertEqual(data.get("status"), "error")

    def test_state_service_corrupted_saved_state_recovery(self):
        """Ensure StateService.get_initial_state recovers cleanly when saved_state is corrupted (non-dict)."""
        corrupted_states = [
            [1, 2, 3],
            [],
            "malformed_json_content",
            12345,
            None
        ]
        for corrupt in corrupted_states:
            self.mock_repo.get_saved_state.return_value = corrupt
            try:
                state = self.state_service.get_initial_state()
            except AttributeError as e:
                self.fail(f"get_initial_state crashed with AttributeError on corrupted state {corrupt!r}: {e}")
            self.assertIsInstance(state, dict)
            self.assertIn("dashboard_inputs", state)

    def test_state_repo_guards_against_non_dict(self):
        """Ensure StateRepository.save_state rejects non-dict objects without touching disk."""
        repo = StateRepository()
        self.assertFalse(repo.save_state([]))
        self.assertFalse(repo.save_state("corrupted"))
        self.assertFalse(repo.save_state(None))


if __name__ == "__main__":
    unittest.main()
