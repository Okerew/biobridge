import unittest
import immune_system
from biobridge.blocks.cell import Cell
from biobridge.enviromental.infection import Infection, InfectionType


class TestImmuneSystem(unittest.TestCase):
    def setUp(self):
        self.Cell = Cell
        self.Infection = Infection
        cells = [
            ("Macro1", 0.8, "Macrophage"),
            ("Macro2", 0.7, "Macrophage"),
            ("TCell1", 0.9, "TCell"),
            ("TCell2", 0.85, "TCell"),
            ("BCell1", 0.75, "BCell"),
            ("BCell2", 0.8, "BCell")
        ]
        self.immune_system = immune_system.ImmuneSystem(self.Cell, cells)

    def test_respond_to_infection(self):
        infection = self.Infection("Test Infection", InfectionType.VIRUS, 0.5, "ATCG")
        cells = [self.Cell(name="TestCell", cell_type="Macrophage", surface_proteins=[], health=100) for _ in range(100)]
        self.immune_system.respond(Infection("Test Infection", InfectionType.VIRUS, 0.5, "ATCG"), cells)
        cells2 = self.immune_system.getCells()
        self.immune_system.visualize(infection, cells2)

        # Check if the spread rate has been reduced
        self.assertLess(infection.spread_rate, 1.0)

        # Check if infected cells have been reduced
        self.assertLess(len(infection.infected_cells), 5)

    def test_cell_activation(self):
        cell = self.Cell(name="TestCell", cell_type="Macrophage", surface_proteins=[], health=100)
        macrophage = immune_system.Macrophage("Macro1", 0.8, cell)
        macrophage.activate()
        macrophage.deactivate()

    def test_cell_attack(self):
        cell = self.Cell(name="TestCell", cell_type="Macrophage", surface_proteins=[], health=100)
        macrophage = immune_system.Macrophage("Macro1", 0.8, cell)
        infection = self.Infection("Test Infection", InfectionType.VIRUS, 0.5, "ATCG")
        macrophage.attack(infection)

        # Check if the spread rate has been reduced
        self.assertLess(infection.spread_rate, 1.0)

        # Check if the cell health has been reduced
        self.assertLess(cell.health, 100)


if __name__ == '__main__':
    unittest.main()
