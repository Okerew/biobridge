from biobridge.blocks.protein import Protein
import random


class TransportProtein(Protein):
    def __init__(self, name, sequence, cargo):
        super().__init__(name, sequence)
        self.cargo = cargo
        self.transport_efficiency = random.uniform(0.3, 0.9)

    def transport(self, cell):
        if self.cargo not in cell.molecules:
            cell.molecules.append(self.cargo)
            return f"{self.name} transported {self.cargo} into the cell"
        return f"{self.cargo} already present in the cell"

    def interact_with_cell(self, cell):
        result = super().interact_with_cell(cell)
        transport_result = self.transport(cell)
        return f"{result} {transport_result}"
