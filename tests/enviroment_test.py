import unittest
from biobridge.blocks.cell import Cell
from biobridge.blocks.tissue import Tissue
from biobridge.enviromental.environment import Environment, Substance


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.cell1 = Cell("Cell 1", health=100)
        self.cell2 = Cell("Cell 2", health=50)
        self.tissue1 = Tissue(name="Tissue 1", cells=[self.cell1, self.cell2], tissue_type="muscular")
        self.drug_A = Substance(name="drug_A", effect={"health": 5})
        self.drug_B = Substance(name="drug_B", effect={"health": -3})
        self.environment = Environment(
            name="Test Environment",
            temperature=25.0,
            humidity=50.0,
            cells=[self.cell1, self.cell2],
            tissues=[self.tissue1],
            environmental_factors={"nutrient": 1.0, "drug_A": 1.0, "drug_B": 0.5},
            substances={"drug_A": self.drug_A, "drug_B": self.drug_B},
            height=10,
            width=10,
        )

    def test_apply_environmental_factors(self):
        self.environment.apply_environmental_factors()
        self.assertEqual(self.cell1.health, 100)  # Nutrient + Drug A - Drug B

    def test_simulate_time_step(self):
        self.environment.simulate_time_step()
        self.assertGreaterEqual(self.cell1.health, 0)
        self.assertGreaterEqual(self.cell2.health, 0)
        self.assertLessEqual(self.cell1.health, 100)
        self.assertLessEqual(self.cell2.health, 100)

    def test_remove_dead_cells(self):
        self.cell2.health = 0
        self.environment.remove_dead_cells()
        self.assertNotIn(self.cell2, self.environment.cells)

    def test_describe(self):
        description = self.environment.describe()
        self.assertIn("Environment Name: Test Environment", description)
        self.assertIn("Temperature: 25.0°C", description)
        self.assertIn("Humidity: 50.0%", description)
        self.assertIn("Number of Cells: 2", description)
        self.assertIn("Number of Tissues: 1", description)
        self.assertIn("Environmental Factors:", description)
        self.assertIn("  nutrient: 1.0", description)
        self.assertIn("  drug_A: 1.0", description)
        self.assertIn("  drug_B: 0.5", description)


if __name__ == '__main__':
    unittest.main()
