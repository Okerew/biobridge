from biobridge.definitions.cells.eukaryotic_cell import EukaryoticCell, Optional, Dict, List, ChromosomePair
from biobridge.genes.dna import DNA



class EpithelialCell(EukaryoticCell):
    def __init__(self, name: str, cell_type: Optional[str] = "epithelial cell", receptors: Optional[List[str]] = None,
                 surface_proteins: Optional[List[str]] = None, organelles: Optional[Dict[str, int]] = None,
                 dna: Optional['DNA'] = None, health: Optional[int] = None,
                 polarity: bool = True, junctions: Optional[Dict[str, bool]] = None, secretion: Optional[Dict[str, float]] = None,
                 chromosome_pairs: Optional[List[ChromosomePair]] = None, age: Optional[int] = 0,
                 metabolism_rate: Optional[float] = 1.0, ph: float = 7.0, osmolarity: float = 300.0,
                 ion_concentrations: Optional[Dict[str, float]] = None, id: Optional[int] = None,
                 structural_integrity: float = 100.0, mutation_count: Optional[int] = 0,
                 growth_rate: Optional[float] = 1.0, repair_rate: Optional[float] = 1.0,
                 max_divisions: Optional[int] = 50):
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
        :param chromosome_pairs: List of chromosome pairs
        :param age: Age of the cell
        :param metabolism_rate: Rate of metabolism
        :param ph: pH level of the cell
        :param osmolarity: Osmolarity of the cell
        :param ion_concentrations: Dictionary of ion concentrations
        :param id: ID of the cell
        :param structural_integrity: Structural integrity of the cell
        :param mutation_count: Number of mutations
        :param growth_rate: Growth rate of the cell
        :param repair_rate: Repair rate of the cell
        :param max_divisions: Maximum number of divisions
        """
        super().__init__(
            name=name,
            cell_type=cell_type,
            receptors=receptors,
            surface_proteins=surface_proteins,
            organelles=organelles,
            dna=dna,
            health=health,
            age=age,
            metabolism_rate=metabolism_rate,
            ph=ph,
            osmolarity=osmolarity,
            ion_concentrations=ion_concentrations,
            id=id,
            structural_integrity=structural_integrity,
            mutation_count=mutation_count,
            growth_rate=growth_rate,
            repair_rate=repair_rate,
            max_divisions=max_divisions,
            chromosome_pairs=chromosome_pairs
        )
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
