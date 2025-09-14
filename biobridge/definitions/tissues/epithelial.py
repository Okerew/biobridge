from typing import List, Optional

from biobridge.definitions.cells.epithelial_cell import EpithelialCell
from biobridge.blocks.tissue import Tissue


class EpithelialTissue(Tissue):
    def __init__(
        self,
        name: str,
        cells: Optional[List[EpithelialCell]] = None,
        cancer_risk: float = 0.001,
    ):
        """
        Initialize a new EpithelialTissue object.

        :param name: Name of the tissue
        :param cells: List of EpithelialCell objects that make up the tissue
        :param cancer_risk: Risk of cancer in this tissue type (default is 0.001)
        """
        super().__init__(name, "epithelial", cells, cancer_risk)
        self.barrier_functionality = True  # Epithelial tissue forms barriers

    def check_barrier_functionality(self) -> bool:
        """
        Check if the epithelial tissue can still form a barrier.

        Returns True if barrier functionality is intact (all cells have functional tight junctions).
        """
        for cell in self.cells:
            if isinstance(cell, EpithelialCell):
                if not cell.junctions.get("tight_junctions", False):
                    self.barrier_functionality = False
                    return False
        self.barrier_functionality = True
        return True

    def regenerate_barrier(self) -> None:
        """
        Attempt to regenerate the epithelial tissue's barrier by adjusting junctions in each cell.
        """
        for cell in self.cells:
            if isinstance(cell, EpithelialCell):
                if not cell.junctions.get("tight_junctions", False):
                    cell.add_junction("tight_junctions")
        self.barrier_functionality = True
        print(f"Barrier regenerated in tissue: {self.name}.")

    def simulate_time_step(self, external_factors: List[tuple] = None) -> None:
        """
        Simulate one time step in the epithelial tissue's life, including growth, healing, and external factors.

        :param external_factors: List of tuples (factor, intensity) to apply
        """
        super().simulate_time_step(external_factors)

        # Check barrier functionality
        if not self.check_barrier_functionality():
            print(f"Warning: Barrier function compromised in {self.name} tissue.")
        else:
            print(f"Barrier function intact in {self.name} tissue.")

    def describe(self) -> str:
        """
        Provide a detailed description of the epithelial tissue.
        """
        base_description = super().describe()
        return (
            base_description
            + f"\nBarrier Functionality: {'Intact' if self.barrier_functionality else 'Compromised'}"
        )

    def __str__(self) -> str:
        """Return a string representation of the epithelial tissue."""
        return self.describe()
