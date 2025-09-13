import unittest
from biobridge.blocks.tissue import Tissue
from biobridge.tools.bioreactor import Bioreactor  # Assuming your class is in biobridge.blocks.bioreactor.py


class TestBioreactor(unittest.TestCase):

    def setUp(self):
        self.bioreactor = Bioreactor(name="Test Bioreactor", capacity=5)
        self.tissue = Tissue(name="Test Tissue", tissue_type="epithelial")  # Assuming Tissue has at least a name attribute

    def test_initialization(self):
        bioreactor = Bioreactor(name="Bio1", capacity=10, temperature=36.5, pH=7.2, oxygen_level=0.18)
        self.assertEqual(bioreactor.name, "Bio1")
        self.assertEqual(bioreactor.capacity, 10)
        self.assertEqual(bioreactor.temperature, 36.5)
        self.assertEqual(bioreactor.pH, 7.2)
        self.assertEqual(bioreactor.oxygen_level, 0.18)
        self.assertEqual(bioreactor.nutrient_level, 1.0)
        self.assertEqual(bioreactor.waste_level, 0.0)
        self.assertEqual(len(bioreactor.tissues), 0)

    def test_add_tissue(self):
        self.bioreactor.add_tissue(self.tissue)
        self.assertIn(self.tissue, self.bioreactor.tissues)
        self.assertEqual(len(self.bioreactor.tissues), 1)

    def test_add_tissue_over_capacity(self):
        for _ in range(self.bioreactor.capacity):
            self.bioreactor.add_tissue(Tissue(name=f"Tissue {_+1}", tissue_type="epithelial"))
        self.bioreactor.add_tissue(self.tissue)
        self.assertEqual(len(self.bioreactor.tissues), self.bioreactor.capacity)  # Should not exceed capacity

    def test_remove_tissue(self):
        self.bioreactor.add_tissue(self.tissue)
        self.bioreactor.remove_tissue(self.tissue)
        self.assertNotIn(self.tissue, self.bioreactor.tissues)
        self.assertEqual(len(self.bioreactor.tissues), 0)

    def test_adjust_temperature(self):
        self.bioreactor.adjust_temperature(35.0)
        self.assertEqual(self.bioreactor.temperature, 35.0)

    def test_adjust_pH(self):
        self.bioreactor.adjust_pH(6.5)
        self.assertEqual(self.bioreactor.pH, 6.5)

    def test_adjust_oxygen_level(self):
        self.bioreactor.adjust_oxygen_level(0.25)
        self.assertEqual(self.bioreactor.oxygen_level, 0.25)

    def test_add_nutrients(self):
        self.bioreactor.add_nutrients(0.5)
        self.assertEqual(self.bioreactor.nutrient_level, 1.0)  # Should not exceed 1.0
        self.bioreactor.nutrient_level = 0.5
        self.bioreactor.add_nutrients(0.3)
        self.assertEqual(self.bioreactor.nutrient_level, 0.8)

    def test_remove_waste(self):
        self.bioreactor.waste_level = 0.5
        self.bioreactor.remove_waste(0.2)
        self.assertEqual(self.bioreactor.waste_level, 0.3)
        self.bioreactor.remove_waste(0.5)
        self.assertEqual(self.bioreactor.waste_level, 0.0)  # Should not go below 0.0

    def test_simulate_time_step(self):
        self.bioreactor.add_tissue(self.tissue)
        self.bioreactor.simulate_time_step()
        self.assertAlmostEqual(self.bioreactor.nutrient_level, 0.9, places=2)
        self.assertAlmostEqual(self.bioreactor.waste_level, 0.05, places=2)

    def test_get_status(self):
        status = self.bioreactor.get_status()
        self.assertIn("Bioreactor: Test Bioreactor", status)
        self.assertIn("Temperature: 37.0°C", status)
        self.assertIn("pH: 7.00", status)
        self.assertIn("Oxygen Level: 0.20", status)
        self.assertIn("Nutrient Level: 1.00", status)
        self.assertIn("Waste Level: 0.00", status)
        self.assertIn("Tissues: 0/5", status)

    def test_str_representation(self):
        str_repr = str(self.bioreactor)
        self.assertEqual(str_repr, self.bioreactor.get_status())

    if __name__ == '__main__':
        unittest.main()
