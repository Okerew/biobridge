from biobridge.definitions.cells.eukaryotic_cell import EukaryoticCell, Optional, Dict, List
from biobridge.genes.dna import DNA


class EpithelialCell(EukaryoticCell):
    def __init__(self, name: str, cell_type: Optional[str] = "epithelial cell", receptors: Optional[List[str]] = None,
                 surface_proteins: Optional[List[str]] = None, organelles: Optional[Dict[str, int]] = None,
                 dna: Optional['DNA'] = None, health: Optional[int] = None,
                 polarity: bool = True, junctions: Optional[Dict[str, bool]] = None, secretion: Optional[Dict[str, float]] = None):
        """
        Initialize a new EpithelialCell object.

        :param name: Name of the cell
        :param cell_type: Type of the cell (default is "epithelial cell")
        :param receptors: List of receptor binding sites on the cell
        :param surface_proteins: List of proteins expressed on the cell surface
        :param organelles: Dictionary of organelles and their quantities
        :param dna: DNA object representing the cell's DNA
        :param health: Health of the cell
        :param polarity: Boolean indicating if the cell has polarity (apical-basal polarity)
        :param junctions: Dictionary indicating the presence of cell junctions (e.g., tight, adherens, gap junctions)
        :param secretion: Dictionary indicating the secretion rates of various substances (e.g., mucus, enzymes)
        """
        super().__init__(name, cell_type, receptors, surface_proteins, organelles, dna, health)
        self.polarity = polarity
        self.junctions = junctions or {
            "tight_junctions": True,
            "adherens_junctions": True,
            "gap_junctions": True,
            "desmosomes": True
        }
        self.secretion = secretion or {}

    def form_barrier(self) -> None:
        """
        Simulate the epithelial cell's ability to form a barrier, such as a skin or mucosal barrier.
        """
        if not self.junctions.get("tight_junctions", False):
            raise ValueError("Tight junctions are required to form an effective barrier.")
        print(f"{self.name} forms a barrier with polarity: {self.polarity}")

    def secrete(self, substance: str, amount: float) -> None:
        """
        Simulate the secretion of a substance by the epithelial cell.

        :param substance: The substance to secrete (e.g., "mucus", "enzyme")
        :param amount: The amount of the substance to secrete
        """
        if substance in self.secretion:
            self.secretion[substance] += amount
        else:
            self.secretion[substance] = amount
        print(f"{self.name} secretes {amount} units of {substance}.")

    def adjust_polarity(self, polarity: bool) -> None:
        """
        Adjust the polarity of the epithelial cell.

        :param polarity: Boolean indicating the new polarity state
        """
        self.polarity = polarity
        print(f"{self.name} polarity adjusted to {'apical-basal' if polarity else 'non-polarized'} state.")

    def add_junction(self, junction_type: str) -> None:
        """
        Add a cell junction type to the epithelial cell.

        :param junction_type: Type of junction to add (e.g., "tight_junctions", "gap_junctions")
        """
        self.junctions[junction_type] = True
        print(f"{junction_type.replace('_', ' ').capitalize()} added to {self.name}.")

    def remove_junction(self, junction_type: str) -> None:
        """
        Remove a cell junction type from the epithelial cell.

        :param junction_type: Type of junction to remove (e.g., "tight_junctions", "gap_junctions")
        """
        if junction_type in self.junctions:
            self.junctions[junction_type] = False
            print(f"{junction_type.replace('_', ' ').capitalize()} removed from {self.name}.")
        else:
            print(f"{junction_type.replace('_', ' ').capitalize()} not found in {self.name}.")

    def describe(self) -> str:
        """Provide a detailed description of the epithelial cell."""
        description = super().describe()
        junctions_status = ", ".join([f"{jt.replace('_', ' ').capitalize()}: {'Present' if status else 'Absent'}"
                                      for jt, status in self.junctions.items()])
        secretion_status = ", ".join([f"{substance}: {amount:.2f} units" for substance, amount in self.secretion.items()])

        epithelial_description = [
            f"Polarity: {'Apical-basal' if self.polarity else 'Non-polarized'}",
            f"Cell Junctions: {junctions_status}",
            f"Secretion: {secretion_status if secretion_status else 'None'}"
        ]
        return description + "\n" + "\n".join(epithelial_description)

    def __str__(self) -> str:
        """Return a string representation of the epithelial cell."""
        return self.describe()
