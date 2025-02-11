from biobridge.blocks.cell import Cell, Optional, List


class GermCell(Cell):
    def __init__(self, name: str, cell_type: str = "germ", ploidy: Optional[int] = 2,
                 meiosis_stage: str = "interphase", gamete_type: Optional[str] = None,
                 **kwargs):
        """
        Initialize a new GermCell object.

        :param name: Name of the cell
        :param cell_type: Type of the cell (default is "germ")
        :param ploidy: Number of chromosome sets (default is 2 for diploid)
        :param meiosis_stage: Current stage of meiosis (default is "interphase")
        :param gamete_type: Type of gamete (e.g., "sperm", "egg", None for immature)
        :param kwargs: Additional parameters to pass to the parent Cell class
        """
        super().__init__(name, cell_type, **kwargs)
        self.ploidy = ploidy
        self.meiosis_stage = meiosis_stage
        self.gamete_type = gamete_type
        self.synaptonemal_complex = []

    def undergo_meiosis(self) -> List['GermCell']:
        """Simulate the meiosis process and return resulting gametes."""
        if self.ploidy != 2:
            raise ValueError("Meiosis can only occur in diploid cells.")

        gametes = []
        for _ in range(4):  # Meiosis typically produces 4 haploid cells
            gamete = GermCell(
                name=f"{self.name}_gamete",
                cell_type="gamete",
                ploidy=1,
                meiosis_stage="completed",
                gamete_type=self.gamete_type,
                chromosomes=[chromosome.replicate() for chromosome in self.chromosomes[:len(self.chromosomes)//2]]
            )
            gametes.append(gamete)

        self.meiosis_stage = "completed"
        return gametes

    def form_synaptonemal_complex(self) -> None:
        """Simulate the formation of the synaptonemal complex during meiosis."""
        if self.meiosis_stage != "prophase I":
            raise ValueError("Synaptonemal complex forms during prophase I of meiosis.")

        self.synaptonemal_complex = [
            (self.chromosomes[i], self.chromosomes[i+1])
            for i in range(0, len(self.chromosomes), 2)
        ]
        print(f"Synaptonemal complex formed with {len(self.synaptonemal_complex)} chromosome pairs.")

    def undergo_crossing_over(self) -> None:
        """Simulate crossing over during meiosis."""
        if not self.synaptonemal_complex:
            raise ValueError("Synaptonemal complex must be formed before crossing over.")

        for chromosome_pair in self.synaptonemal_complex:
            # Simplified crossing over: swap some genetic material
            crossover_point = len(chromosome_pair[0].dna.sequence) // 2
            temp = chromosome_pair[0].dna.sequence[:crossover_point]
            chromosome_pair[0].dna.sequence = chromosome_pair[1].dna.sequence[:crossover_point] + chromosome_pair[0].dna.sequence[crossover_point:]
            chromosome_pair[1].dna.sequence = temp + chromosome_pair[1].dna.sequence[crossover_point:]

        print("Crossing over completed.")

    def differentiate_gamete(self, gamete_type: str) -> None:
        """
        Differentiate the germ cell into a specific type of gamete.

        :param gamete_type: The type of gamete to differentiate into ("sperm" or "egg")
        """
        if gamete_type not in ["sperm", "egg"]:
            raise ValueError("Gamete type must be either 'sperm' or 'egg'")

        self.gamete_type = gamete_type
        self.cell_type = f"{gamete_type}_cell"

        if gamete_type == "sperm":
            self.add_organelle("acrosome")
            self.add_organelle("flagellum")
        elif gamete_type == "egg":
            self.add_organelle("cortical granules")
            # Eggs typically have more mitochondria
            self.add_mitochondrion(quantity=1000)

        print(f"Germ cell differentiated into {gamete_type} cell.")

    def describe(self) -> str:
        """Provide a detailed description of the germ cell."""
        description = super().describe()
        germ_cell_info = f"""
        Germ Cell Specific Information:
        Ploidy: {self.ploidy}
        Meiosis Stage: {self.meiosis_stage}
        Gamete Type: {self.gamete_type or 'Undifferentiated'}
        Synaptonemal Complex: {'Formed' if self.synaptonemal_complex else 'Not formed'}
        """
        return description + germ_cell_info

    def to_dict(self) -> dict:
        """Return a dictionary representation of the germ cell."""
        germ_cell_dict = super().to_dict()
        germ_cell_dict.update({
            'ploidy': self.ploidy,
            'meiosis_stage': self.meiosis_stage,
            'gamete_type': self.gamete_type,
            'synaptonemal_complex': bool(self.synaptonemal_complex)
        })
        return germ_cell_dict

    @classmethod
    def from_dict(cls, cell_dict: dict) -> 'GermCell':
        """Create a GermCell object from a dictionary."""
        cell = super().from_dict(cell_dict)
        germ_cell = cls(name="GermCell", cell_type="germ")
        germ_cell.__dict__.update(cell.__dict__)  # copy attributes from Cell object
        germ_cell.ploidy = cell_dict['ploidy']
        germ_cell.meiosis_stage = cell_dict['meiosis_stage']
        germ_cell.gamete_type = cell_dict['gamete_type']
        germ_cell.synaptonemal_complex = [] if cell_dict['synaptonemal_complex'] else None
        return germ_cell
