from typing import Optional, List, Dict
from biobridge.genes.dna import DNA
from biobridge.definitions.cells.eukaryotic_cell import EukaryoticCell, json


class SomaticCell(EukaryoticCell):
    def __init__(self, name: str, cell_type: Optional[str] = "Somatic", receptors: Optional[List[str]] = None,
                 surface_proteins: Optional[List[str]] = None, organelles: Optional[Dict[str, int]] = None,
                 dna: Optional['DNA'] = None, health: Optional[int] = None,
                 division_count: int = 0, telomere_length: int = 100):
        super().__init__(name, cell_type, receptors, surface_proteins, organelles, dna, health)
        self.division_count = division_count
        self.telomere_length = telomere_length

    def mitotic_division(self) -> 'SomaticCell':
        """
        Perform mitotic cell division, creating a new somatic cell with identical DNA.

        :return: A new SomaticCell object
        """
        # Check if the cell can divide
        if self.telomere_length <= 0 or self.health < 50:
            print(f"{self.name} cannot divide due to short telomeres or low health.")
            return

        # Create a new cell with the same properties
        new_cell = SomaticCell(
            name=f"{self.name}_daughter",
            cell_type=self.cell_type,
            receptors=self.receptors.copy(),
            surface_proteins=self.surface_proteins.copy(),
            organelles=self.organelles.copy(),
            dna=self.dna.replicate() if self.dna else None,
            division_count=self.division_count + 1,
            telomere_length=self.telomere_length - 1
        )

        # Update the parent cell
        self.division_count += 1
        self.telomere_length -= 1
        self.health -= 20  # Mitotic division takes more energy than simple division

        print(f"{self.name} has undergone mitotic division. A new daughter cell has been created.")
        return new_cell

    def describe(self) -> str:
        """Provide a detailed description of the somatic cell."""
        description = super().describe()
        additional_info = f"\nDivision Count: {self.division_count}\nTelomere Length: {self.telomere_length}"
        return description + additional_info

    def to_json(self) -> str:
        """Return a JSON representation of the somatic cell."""
        somatic_cell_dict = super().__dict__.copy()
        somatic_cell_dict.update({
            "division_count": self.division_count,
            "telomere_length": self.telomere_length
        })
        return json.dumps(somatic_cell_dict)

    @classmethod
    def from_json(cls, json_str: str) -> 'SomaticCell':
        """Load a somatic cell from a JSON string."""
        cell_dict = json.loads(json_str)
        somatic_cell = cls(
            name=cell_dict['name'],
            cell_type=cell_dict['cell_type'],
            receptors=cell_dict['receptors'],
            surface_proteins=cell_dict['surface_proteins'],
            organelles=cell_dict['organelles'],
            dna=cell_dict['dna'] if 'dna' in cell_dict else None,
            division_count=cell_dict['division_count'],
            telomere_length=cell_dict['telomere_length']
        )
        return somatic_cell
