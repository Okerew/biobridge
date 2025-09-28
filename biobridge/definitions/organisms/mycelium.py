from typing import List, Optional
from biobridge.blocks.cell import Cell, DNA, Chromosome, Protein
import random


class Spore(Cell):
    def __init__(self, name: str, dna: Optional[DNA] = None, chromosomes: Optional[List[Chromosome]] = None,
                 dormancy_period: int = 0, germination_rate: float = 0.5, resistance: float = 1.0):
        super().__init__(name, cell_type="fungal_spore", dna=dna, chromosomes=chromosomes)
        self.dormancy_period = dormancy_period  # Period of dormancy in days
        self.germination_rate = germination_rate  # Probability of germination under favorable conditions
        self.resistance = resistance  # Resistance to environmental stressors (1.0 is normal, higher is more resistant)

        # Add spore-specific proteins
        spore_coat_protein = Protein("Spore Coat Protein", "MSLLPKRYGGPFGCRRYWNCPYCNP")
        self.add_surface_protein(spore_coat_protein)

    def germinate(self) -> bool:
        """
        Attempt to germinate the spore.

        :return: True if germination is successful, False otherwise
        """
        if self.dormancy_period > 0:
            self.dormancy_period -= 1
            return False

        if random.random() < self.germination_rate:
            self.cell_type = "fungal_hypha"
            return True
        return False

    def resist_stress(self, stress_level: float) -> None:
        """
        Resist environmental stress.

        :param stress_level: Level of environmental stress
        """
        damage = stress_level / self.resistance
        self.health -= damage
        self.health = max(0, min(100, self.health))

    def describe(self) -> str:
        """Provide a detailed description of the spore."""
        description = super().describe()
        spore_info = f"\nSpore-specific info:\n" \
                     f"Dormancy period: {self.dormancy_period} days\n" \
                     f"Germination rate: {self.germination_rate:.2f}\n" \
                     f"Resistance: {self.resistance:.2f}"
        return description + spore_info


class Mushroom:
    def __init__(self, name: str, species: str, cap_diameter: float, stem_height: float,
                 is_edible: bool, spore_color: str):
        self.name = name
        self.species = species
        self.cap_diameter = cap_diameter  # in cm
        self.stem_height = stem_height  # in cm
        self.is_edible = is_edible
        self.spore_color = spore_color
        self.hypha_network = []  # List to store connected hyphae

    def produce_spores(self, num_spores: int) -> List[Spore]:
        """
        Produce a given number of spores.

        :param num_spores: Number of spores to produce
        :return: List of produced Spore objects
        """
        spores = []
        for i in range(num_spores):
            spore_name = f"{self.name}_spore_{i + 1}"
            spore_dna = DNA("ATCG" * 25)  # Simplified DNA sequence
            spore_chromosome = Chromosome(spore_dna, "Fungal Chromosome 1")
            spore = Spore(spore_name, dna=spore_dna, chromosomes=[spore_chromosome])
            spores.append(spore)
        return spores

    def grow(self, growth_rate: float) -> None:
        """
        Grow the mushroom.

        :param growth_rate: Rate of growth
        """
        self.cap_diameter += growth_rate
        self.stem_height += growth_rate * 0.5

    def connect_hypha(self, hypha: 'Hypha') -> None:
        """
        Connect a hypha to the mushroom's network.

        :param hypha: Hypha object to connect
        """
        self.hypha_network.append(hypha)

    def describe(self) -> str:
        """Provide a detailed description of the mushroom."""
        description = f"Mushroom: {self.name}\n" \
                      f"Species: {self.species}\n" \
                      f"Cap diameter: {self.cap_diameter:.2f} cm\n" \
                      f"Stem height: {self.stem_height:.2f} cm\n" \
                      f"Edible: {'Yes' if self.is_edible else 'No'}\n" \
                      f"Spore color: {self.spore_color}\n" \
                      f"Connected hyphae: {len(self.hypha_network)}"
        return description


class Hypha(Cell):
    def __init__(self, name: str, length: float = 0.0, branching_factor: float = 0.1):
        super().__init__(name, cell_type="fungal_hypha")
        self.length = length  # in micrometers
        self.branching_factor = branching_factor
        self.branches = []

    def grow(self, growth_rate: float) -> None:
        """
        Grow the hypha.

        :param growth_rate: Rate of growth
        """
        self.length += growth_rate
        if random.random() < self.branching_factor:
            self.branch()

    def branch(self) -> None:
        """Create a new branch from this hypha."""
        branch_name = f"{self.name}_branch_{len(self.branches) + 1}"
        new_branch = Hypha(branch_name, length=0, branching_factor=self.branching_factor * 0.9)
        self.branches.append(new_branch)

    def describe(self) -> str:
        """Provide a detailed description of the hypha."""
        description = super().describe()
        hypha_info = f"\nHypha-specific info:\n" \
                     f"Length: {self.length:.2f} micrometers\n" \
                     f"Branching factor: {self.branching_factor:.2f}\n" \
                     f"Number of branches: {len(self.branches)}"
        return description + hypha_info
    