import unittest
import json
from biobridge.blocks.tissue import Tissue
from biobridge.blocks.cell import Cell


class TestTissue(unittest.TestCase):
    def setUp(self):
        self.tissue = Tissue("Test Tissue", "epithelial")
        self.cells = [
            Cell("Cell 1", cell_type="Epithelial Cell",),
            Cell("Cell 2", cell_type="Epithelial Cell",),
            Cell("Cell 3", cell_type="Epithelial Cell",)
        ]
        for cell in self.cells:
            self.tissue.add_cell(cell)

    def test_init(self):
        self.assertEqual(self.tissue.name, "Test Tissue")
        self.assertEqual(self.tissue.tissue_type, "epithelial")
        self.assertEqual(len(self.tissue.cells), 3)

    def test_add_cell(self):
        new_cell = Cell("New Cell", cell_type="Epithelial Cell",)
        self.tissue.add_cell(new_cell)
        self.assertEqual(len(self.tissue.cells), 4)
        self.assertIn(new_cell, self.tissue.cells)
        custom_weights = {
            'water': 1e12,
            'cell_membrane': 2e9,
            'organelles': 5e11,
            'cell_volume': 1e12
        }
        print(self.tissue.calculate_molecular_weight(custom_weights))

    def test_remove_cell(self):
        cell_to_remove = self.cells[1]
        self.tissue.remove_cell(cell_to_remove)
        self.assertEqual(len(self.tissue.cells), 2)
        self.assertNotIn(cell_to_remove, self.tissue.cells)

    def test_get_cell_count(self):
        self.assertEqual(self.tissue.get_cell_count(), 3)

    def test_get_average_cell_health(self):
        expected_avg_health = (100 + 80 + 90) / 3
        self.assertAlmostEqual(self.tissue.get_average_cell_health(), expected_avg_health)

    def test_tissue_metabolism(self):
        initial_health = [cell.health for cell in self.tissue.cells]
        self.tissue.tissue_metabolism()
        for i, cell in enumerate(self.tissue.cells):
            self.assertLess(cell.health, initial_health[i])

    def test_tissue_repair(self):
        repair_amount = 10
        initial_health = [cell.health for cell in self.tissue.cells]
        self.tissue.tissue_repair(repair_amount)
        for i, cell in enumerate(self.tissue.cells):
            self.assertEqual(cell.health, min(initial_health[i] + repair_amount, 100))

    def test_simulate_cell_division(self):
        initial_cell_count = len(self.tissue.cells)
        self.tissue.simulate_cell_division()
        self.assertGreaterEqual(len(self.tissue.cells), initial_cell_count)

    def test_apply_stress(self):
        stress_amount = 20
        initial_health = [cell.health for cell in self.tissue.cells]
        self.tissue.apply_stress(stress_amount)
        for i, cell in enumerate(self.tissue.cells):
            self.assertLess(cell.health, initial_health[i])
            self.assertGreaterEqual(cell.health, 0)

    def test_remove_dead_cells(self):
        dead_cell = Cell("Dead Cell", cell_type="Epithelial Cell",)
        self.tissue.add_cell(dead_cell)
        initial_cell_count = len(self.tissue.cells)
        self.tissue.remove_dead_cells()
        self.assertEqual(len(self.tissue.cells), initial_cell_count - 1)
        self.assertNotIn(dead_cell, self.tissue.cells)

    def test_describe(self):
        description = self.tissue.describe()
        self.assertIn("Test Tissue", description)
        self.assertIn("epithelial", description)
        self.assertIn("Number of Cells: 3", description)

    def test_to_json(self):
        json_str = self.tissue.to_json()
        tissue_dict = json.loads(json_str)
        self.assertEqual(tissue_dict['name'], "Test Tissue")
        self.assertEqual(tissue_dict['tissue_type'], "epithelial")
        self.assertEqual(len(tissue_dict['cells']), 3)

    def test_from_json(self):
        json_str = self.tissue.to_json()
        new_tissue = Tissue.from_json(json_str)
        self.assertEqual(new_tissue.name, self.tissue.name)
        self.assertEqual(new_tissue.tissue_type, self.tissue.tissue_type)
        self.assertEqual(len(new_tissue.cells), len(self.tissue.cells))


if __name__ == '__main__':
    unittest.main()
