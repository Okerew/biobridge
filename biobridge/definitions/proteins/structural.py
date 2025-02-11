from biobridge.blocks.protein import Protein
import random


class StructuralProtein(Protein):
    def __init__(self, name, sequence, location):
        super().__init__(name, sequence)
        self.location = location
        self.strength = random.uniform(0.5, 1.0)

    def provide_structure(self, cell):
        cell.update_structural_integrity()
        cell.structural_integrity += self.strength
        return f"{self.name} improved cell structural integrity in {self.location}"

    def interact_with_cell(self, cell):
        result = super().interact_with_cell(cell)
        structure_result = self.provide_structure(cell)
        return f"{result} {structure_result}"
