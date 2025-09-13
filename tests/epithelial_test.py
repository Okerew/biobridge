import unittest
from unittest.mock import patch, MagicMock
from biobridge.blocks.cell import Cell
from biobridge.definitions.cells.epithelial_cell import EpithelialCell
from biobridge.definitions.tissues.epithelial import EpithelialTissue

class TestEpithelialTissue(unittest.TestCase):

    def setUp(self):
        self.cell1 = EpithelialCell(name="Cell1", junctions={"tight_junctions": True})
        self.cell2 = EpithelialCell(name="Cell2", junctions={"tight_junctions": False})
        self.cells = [self.cell1, self.cell2]
        self.tissue = EpithelialTissue(name="TestTissue", cells=self.cells)

    def test_initialization(self):
        self.assertEqual(self.tissue.name, "TestTissue")
        self.assertEqual(self.tissue.cell_type, "epithelial")
        self.assertEqual(self.tissue.cells, self.cells)
        self.assertEqual(self.tissue.cancer_risk, 0.001)
        self.assertTrue(self.tissue.barrier_functionality)

    def test_check_barrier_functionality(self):
        self.assertFalse(self.tissue.check_barrier_functionality())
        self.cell2.junctions["tight_junctions"] = True
        self.assertTrue(self.tissue.check_barrier_functionality())

    def test_regenerate_barrier(self):
        self.tissue.regenerate_barrier()
        for cell in self.tissue.cells:
            self.assertTrue(cell.junctions.get("tight_junctions", False))
        self.assertTrue(self.tissue.barrier_functionality)

    @patch('builtins.print')
    def test_simulate_time_step(self, mock_print):
        self.tissue.simulate_time_step()
        mock_print.assert_called_with("Warning: Barrier function compromised in TestTissue tissue.")

        self.cell2.junctions["tight_junctions"] = True
        self.tissue.simulate_time_step()
        mock_print.assert_called_with("Barrier function intact in TestTissue tissue.")

    def test_describe(self):
        description = self.tissue.describe()
        self.assertIn("Barrier Functionality: Compromised", description)

        self.cell2.junctions["tight_junctions"] = True
        description = self.tissue.describe()
        self.assertIn("Barrier Functionality: Intact", description)

    def test_str(self):
        self.assertIn("Barrier Functionality: Compromised", str(self.tissue))

        self.cell2.junctions["tight_junctions"] = True
        self.assertIn("Barrier Functionality: Intact", str(self.tissue))

if __name__ == '__main__':
    unittest.main()
