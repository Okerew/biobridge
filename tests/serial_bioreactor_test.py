import unittest
from unittest.mock import MagicMock, patch
from biobridge.control.serial.bioreactor import BioreactorSerialManager
from biobridge.blocks.tissue import Tissue


class TestBioreactorManager(unittest.TestCase):
    @patch('serial.Serial')
    def setUp(self, mock_serial):
        self.mock_conn = MagicMock()
        mock_serial.return_value = self.mock_conn
        self.bioreactor = BioreactorSerialManager(port="COM3")
        self.bioreactor.connect()

    def tearDown(self):
        self.bioreactor.disconnect()

    def test_connect_and_disconnect(self):
        self.assertTrue(self.bioreactor.serial_conn.is_open)
        self.bioreactor.disconnect()
        self.mock_conn.close.assert_called_once()

    def test_add_and_remove_tissue(self):
        tissue = Tissue("TestTissue", "epithelial")
        self.bioreactor.add_tissue(tissue)
        self.assertIn("TestTissue", self.bioreactor.tissues)

        self.bioreactor.remove_tissue("TestTissue")
        self.assertNotIn("TestTissue", self.bioreactor.tissues)

    def test_set_temperature(self):
        self.mock_conn.readline.return_value = b'OK\n'
        self.bioreactor.set_temperature(37.5)
        self.mock_conn.write.assert_called_with(b'SET_TEMP:37.5')
        self.assertEqual(self.bioreactor.temperature, 37.5)

    def test_set_pH(self):
        self.mock_conn.readline.return_value = b'OK\n'
        self.bioreactor.set_pH(7.2)
        self.mock_conn.write.assert_called_with(b'SET_PH:7.20')
        self.assertEqual(self.bioreactor.pH, 7.2)

    def test_add_nutrients(self):
        self.mock_conn.readline.return_value = b'OK\n'
        initial_level = self.bioreactor.nutrient_level
        self.bioreactor.add_nutrients(10)
        self.mock_conn.write.assert_called_with(b'ADD_NUTRIENTS:10.0')
        self.assertEqual(self.bioreactor.nutrient_level, min(100, initial_level + 10))

    @patch('random.uniform')
    def test_simulate_time_step(self, mock_random):
        mock_random.return_value = 2.5
        tissue = MagicMock()
        self.bioreactor.tissues["TestTissue"] = tissue
        self.bioreactor.simulate_time_step()
        tissue.simulate_time_step.assert_called_once()
        tissue.apply_external_factor.assert_called()
        self.assertLess(self.bioreactor.nutrient_level, 100)

    def test_get_tissue_status(self):
        tissue = Tissue("TestTissue", "epithelial")
        self.bioreactor.add_tissue(tissue)
        status = self.bioreactor.get_tissue_status("TestTissue")
        self.assertIn("TestTissue", status)
        self.assertIn("epithelial", status)

    def test_get_all_tissue_status(self):
        tissue1 = Tissue("TestTissue1", "epithelial")
        tissue2 = Tissue("TestTissue2", "muscle")
        self.bioreactor.add_tissue(tissue1)
        self.bioreactor.add_tissue(tissue2)
        status = self.bioreactor.get_all_tissue_status()
        self.assertIn("TestTissue1", status)
        self.assertIn("TestTissue2", status)
        self.assertIn("epithelial", status)
        self.assertIn("muscle", status)

    @patch('random.random')
    @patch('random.uniform')
    def test_run_experiment(self, mock_uniform, mock_random):
        mock_random.return_value = 0.05  # Ensure external factor is applied
        mock_uniform.return_value = 0.3  # Set a consistent random value
        tissue = Tissue("TestTissue", "epithelial")
        self.bioreactor.add_tissue(tissue)
        self.bioreactor.run_experiment(duration=5, interval=1)
        self.assertGreater(mock_uniform.call_count, 0)


if __name__ == '__main__':
    unittest.main()