import random
from biobridge.blocks.protein import Protein


class Virus:
    def __init__(self, name, genome, proteins=None):
        self.name = name
        self.genome = genome
        self.proteins = proteins or []
        self.host_cells = []
        self.mutation_rate = 0.001
        self.replication_rate = 1.0
        self.virulence = 0.5

    def add_protein(self, protein):
        if isinstance(protein, Protein):
            self.proteins.append(protein)
        else:
            raise TypeError("Must be a Protein object")

    def mutate(self):
        """Simulate mutation in the virus genome."""
        mutated_genome = ""
        for base in self.genome:
            if random.random() < self.mutation_rate:
                mutated_genome += random.choice('ATCG')
            else:
                mutated_genome += base
        self.genome = mutated_genome

    def replicate(self):
        """Simulate virus replication."""
        num_new_viruses = int(self.replication_rate * len(self.host_cells))
        return [Virus(f"{self.name}-offspring", self.genome) for _ in range(num_new_viruses)]

    def infect(self, cell):
        """Simulate infection of a host cell."""
        if cell not in self.host_cells:
            self.host_cells.append(cell)
            infection_chance = random.random()
            if infection_chance < self.virulence:
                print(f"{self.name} successfully infected {cell}")
                return True
            else:
                print(f"{self.name} failed to infect {cell}")
                return False

    def release_from_cell(self, cell):
        """Simulate the release of new viruses from an infected cell."""
        if cell in self.host_cells:
            self.host_cells.remove(cell)
            return self.replicate()
        return []

    def adapt_to_environment(self):
        """Simulate adaptation to a new environment."""
        adaptation_factor = random.uniform(0.8, 1.2)
        self.replication_rate *= adaptation_factor
        self.virulence *= adaptation_factor

    def __str__(self):
        return f"Virus: {self.name}\nGenome: {self.genome[:50]}...\nProteins: {len(self.proteins)}\nHost Cells: {len(self.host_cells)}"

    def get_basic_reproduction_number(self):
        """Calculate the basic reproduction number (R0)."""
        return self.replication_rate * self.virulence * len(self.host_cells)
