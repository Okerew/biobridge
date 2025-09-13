from biobridge.blocks.protein import Protein
import random


class EnzymeProtein(Protein):
    def __init__(self, name, sequence, substrate, product):
        super().__init__(name, sequence)
        self.substrate = substrate
        self.product = product
        self.catalytic_rate = random.uniform(0.1, 1.0)

    def catalyze(self, cell):
        if self.substrate in cell.molecules:
            cell.molecules.remove(self.substrate)
            cell.molecules.append(self.product)
            return f"{self.name} catalyzed the conversion of {self.substrate} to {self.product}"
        return f"No {self.substrate} available for {self.name} to catalyze"

    def interact_with_cell(self, cell):
        result = super().interact_with_cell(cell)
        catalysis_result = self.catalyze(cell)
        return f"{result} {catalysis_result}"
