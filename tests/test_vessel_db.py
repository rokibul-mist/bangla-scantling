import unittest
import os
import shutil
import tempfile
from app.repositories.vessel_repository import VesselRepository
from app.repositories.state_repository import StateRepository
from app.services.vessel_service import VesselService

class TestVesselDatabase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.state_repo = StateRepository()
        self.vessel_repo = VesselRepository(base_dir=self.test_dir)
        self.vessel_service = VesselService(
            vessel_repo=self.vessel_repo,
            state_repo=self.state_repo
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_and_list_vessels(self):
        state = self.state_repo.get_state()
        saved = self.vessel_service.save_vessel_from_state(
            state,
            custom_meta={
                "vessel_name": "Test Vessel Alpha",
                "owner": "Test Owner",
                "notes": "Testing database save functionality"
            }
        )
        self.assertIsNotNone(saved)
        self.assertEqual(saved['vessel_name'], "Test Vessel Alpha")

        vessels = self.vessel_service.list_vessels()
        self.assertGreaterEqual(len(vessels), 1)
        found = next((v for v in vessels if v['id'] == saved['id']), None)
        self.assertIsNotNone(found)
        self.assertEqual(found['vessel_name'], "Test Vessel Alpha")

    def test_get_vessel_and_load(self):
        state = self.state_repo.get_state()
        saved = self.vessel_service.save_vessel_from_state(
            state,
            custom_meta={"vessel_name": "Test Vessel Beta"}
        )
        v_id = saved['id']
        full = self.vessel_service.get_vessel(v_id)
        self.assertIsNotNone(full)
        self.assertIn('state_data', full)
        self.assertEqual(full['vessel_name'], "Test Vessel Beta")

        loaded = self.vessel_service.load_vessel_into_workspace(v_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded['active_vessel_id'], v_id)

    def test_duplicate_and_delete_vessel(self):
        state = self.state_repo.get_state()
        saved = self.vessel_service.save_vessel_from_state(
            state,
            custom_meta={"vessel_name": "Original Vessel"}
        )
        v_id = saved['id']

        cloned = self.vessel_service.duplicate_vessel(v_id, new_name="Cloned Vessel")
        self.assertIsNotNone(cloned)
        self.assertEqual(cloned['vessel_name'], "Cloned Vessel")
        self.assertNotEqual(cloned['id'], v_id)

        # Delete original
        deleted = self.vessel_service.delete_vessel(v_id)
        self.assertTrue(deleted)

        # Check list
        vessels = self.vessel_service.list_vessels()
        self.assertIsNone(next((v for v in vessels if v['id'] == v_id), None))
        self.assertIsNotNone(next((v for v in vessels if v['id'] == cloned['id']), None))

if __name__ == '__main__':
    unittest.main()
