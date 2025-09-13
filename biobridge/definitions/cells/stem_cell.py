from typing import List, Dict, Optional
import random
from biobridge.definitions.cells.eukaryotic_cell import EukaryoticCell
from biobridge.genes.dna import DNA


class StemCell(EukaryoticCell):
    def __init__(self, name: str, cell_type: Optional[str] = "stem cell", receptors: Optional[List[str]] = None,
                 surface_proteins: Optional[List[str]] = None, organelles: Optional[Dict[str, int]] = None,
                 dna: Optional['DNA'] = None, health: Optional[int] = None,
                 differentiation_potential: float = 100.0, pluripotency: bool = True, self_renewal: bool = True):
        """
        Initialize a new StemCell object.

        :param name: Name of the cell
        :param cell_type: Type of the cell (default is "stem cell")
        :param receptors: List of receptor binding sites on the cell
        :param surface_proteins: List of proteins expressed on the cell surface
        :param organelles: Dictionary of organelles and their quantities
        :param dna: DNA object representing the cell's DNA
        :param health: Health of the cell
        :param differentiation_potential: Potential of the stem cell to differentiate into other cell types (0-100)
        :param pluripotency: Boolean indicating if the cell is pluripotent
        :param self_renewal: Boolean indicating if the cell has self-renewal capabilities
        """
        super().__init__(name, cell_type, receptors, surface_proteins, organelles, dna, health
                         )
        self.differentiation_potential = differentiation_potential
        self.pluripotency = pluripotency
        self.self_renewal = self_renewal

    def differentiate(self, target_cell_type: str) -> 'EukaryoticCell':
        """
        Differentiate the stem cell into a specific cell type.

        :param target_cell_type: The type of cell to differentiate into (e.g., "neuron", "muscle cell")
        :return: A new Cell object of the specified type
        """
        if not self.pluripotency:
            raise ValueError("This stem cell is not pluripotent and cannot differentiate into other cell types.")

        # Decrease differentiation potential as the cell differentiates
        self.differentiation_potential -= random.uniform(10.0, 30.0)
        self.differentiation_potential = max(0, int(self.differentiation_potential))

        # If differentiation potential drops to zero, the cell loses pluripotency
        if self.differentiation_potential == 0:
            self.pluripotency = False

        # Create a new differentiated cell
        new_cell = EukaryoticCell(
            name=f"{self.name}_{target_cell_type}",
            cell_type=target_cell_type,
            receptors=self.receptors.copy(),
            surface_proteins=self.surface_proteins.copy(),
            organelles=self.organelles.copy(),
            dna=self.dna.replicate() if self.dna else None,
            health=self.health
        )
        return new_cell

    def self_renew(self) -> 'StemCell':
        """
        Simulate the self-renewal of the stem cell, creating a new stem cell with similar properties.

        :return: A new StemCell object
        """
        if not self.self_renewal:
            raise ValueError("This stem cell does not have self-renewal capabilities.")

        new_stem_cell = StemCell(
            name=f"{self.name}_offspring",
            receptors=self.receptors.copy(),
            surface_proteins=self.surface_proteins.copy(),
            organelles=self.organelles.copy(),
            dna=self.dna.replicate() if self.dna else None,
            health=self.health,
            differentiation_potential=self.differentiation_potential,
            pluripotency=self.pluripotency,
            self_renewal=self.self_renewal
        )
        return new_stem_cell

    def lose_pluripotency(self) -> None:
        """
        Simulate the loss of pluripotency in the stem cell.
        """
        self.pluripotency = False
        self.differentiation_potential = 0.0

    def describe(self) -> str:
        """Provide a detailed description of the stem cell."""
        description = super().describe()
        stem_cell_description = [
            f"Differentiation Potential: {self.differentiation_potential:.2f}",
            f"Pluripotency: {'Yes' if self.pluripotency else 'No'}",
            f"Self-Renewal: {'Yes' if self.self_renewal else 'No'}"
        ]
        return description + "\n" + "\n".join(stem_cell_description)

    def __str__(self) -> str:
        """Return a string representation of the stem cell."""
        return self.describe()
