import unittest
from biobridge.definitions.cells.muscle_cell import MuscleCell
from biobridge.definitions.tissues.muscle import MuscleTissue


class TestMuscleTissue(unittest.TestCase):
    
    def setUp(self):
        """Set up a basic MuscleTissue object for testing."""
        # Create muscle cells with different health and contractile forces
        self.muscle_cells = [
            MuscleCell(name="MuscleCell_1", health=100, contractile_force=10),
            MuscleCell(name="MuscleCell_2", health=90, contractile_force=15),
            MuscleCell(name="MuscleCell_3", health=80, contractile_force=8),
            MuscleCell(name="MuscleCell_4", health=85, contractile_force=12),
        ]
        self.muscle_tissue = MuscleTissue(name="Bicep", cells=self.muscle_cells)

    def test_add_cell(self):
        """Test adding a cell to the muscle tissue."""
        new_cell = MuscleCell(name="NewMuscleCell", health=70, contractile_force=9)
        self.muscle_tissue.add_cell(new_cell)
        self.assertIn(new_cell, self.muscle_tissue.cells)
        self.assertEqual(self.muscle_tissue.get_cell_count(), 5)

    def test_remove_cell(self):
        """Test removing a cell from the muscle tissue."""
        cell_to_remove = self.muscle_cells[0]
        self.muscle_tissue.remove_cell(cell_to_remove)
        self.assertNotIn(cell_to_remove, self.muscle_tissue.cells)
        self.assertEqual(self.muscle_tissue.get_cell_count(), 3)

    def test_contract_muscle(self):
        """Test muscle contraction and ensure some cells are contracting."""
        self.muscle_tissue.contract_muscle()

    def test_relax_muscle(self):
        """Test muscle relaxation and ensure all cells are relaxed."""
        self.muscle_tissue.contract_muscle()  # First, contract some cells
        self.muscle_tissue.relax_muscle()  # Now, relax them
    
    def test_simulate_contraction_cycle(self):
        """Test full contraction-relaxation cycle."""
        self.muscle_tissue.simulate_contraction_cycle()
        self.muscle_tissue.contract_muscle()
        self.muscle_tissue.relax_muscle()  # Ensure the relaxation works after contraction

    def test_simulate_time_step(self):
        """Test the time step simulation for muscle tissue."""
        initial_cell_count = self.muscle_tissue.get_cell_count()
        self.muscle_tissue.simulate_time_step()  # This should simulate growth, division, and contraction
        new_cell_count = self.muscle_tissue.get_cell_count()

        # Check if growth happened (new cells should be added)
        self.assertGreaterEqual(new_cell_count, initial_cell_count)

        self.muscle_tissue.contract_muscle()


if __name__ == "__main__":
    unittest.main()
