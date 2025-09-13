import random
from typing import List, Optional
from biobridge.blocks.cell import Cell
from biobridge.blocks.tissue import Tissue


class RadiationAffectedTissue(Tissue):
    def __init__(self, name: str, tissue_type: str, cells: Optional[List[Cell]] = None,
                 cancer_risk: float = 0.005, mutation_rate: Optional[float] = 0.01, radiation_level: float = 0.0):
        """
        Initialize a new RadiationAffectedTissue object.

        :param name: Name of the tissue
        :param tissue_type: Type of the tissue
        :param cells: List of Cell objects that make up the tissue
        :param cancer_risk: Risk of cancer development (default is higher due to radiation)
        :param radiation_level: Current level of radiation exposure (0.0 to 1.0)
        """
        super().__init__(name, tissue_type, cells, cancer_risk)
        self.radiation_level = radiation_level
        self.mutation_rate = mutation_rate
        self.dna_repair_rate = 0.05  # Base DNA repair rate

    def apply_radiation(self, intensity: float) -> None:
        """
        Apply radiation to the tissue, affecting cell health and potentially causing mutations.

        :param intensity: The intensity of radiation exposure (0.0 to 1.0)
        """
        self.radiation_level = min(1.0, self.radiation_level + intensity)
        for cell in self.cells:
            cell.health -= intensity * 30  # Radiation causes more damage than generic external factors
            cell.health = max(0, cell.health)
            if random.random() < self.mutation_rate * intensity:
                cell.mutate()

    def simulate_dna_repair(self) -> None:
        """Simulate DNA repair mechanisms in radiation-affected cells."""
        for cell in self.cells:
            if cell.is_mutated and random.random() < self.dna_repair_rate:
                cell.repair_mutation()

    def calculate_mutation_rate(self) -> float:
        """Calculate the current mutation rate based on radiation level."""
        return self.mutation_rate * (1 + self.radiation_level * 5)  # Radiation increases mutation rate

    def simulate_cell_division(self) -> None:
        """Override cell division to account for radiation effects."""
        new_cells = []
        for cell in self.cells:
            if cell.health > 70 and random.random() < 0.1:  # 10% chance of division for healthy cells
                new_cell = cell.divide()
                if random.random() < self.calculate_mutation_rate():
                    new_cell.mutate()
                new_cells.append(new_cell)
        self.cells.extend(new_cells)

    def simulate_time_step(self, external_factors: List[tuple] = None) -> None:
        """
        Simulate one time step in the radiation-affected tissue's life.

        :param external_factors: List of tuples (factor, intensity) to apply
        """
        super().simulate_time_step(external_factors)
        self.simulate_dna_repair()
        self.radiation_level *= 0.95  # Natural decay of radiation level over time

    def describe(self) -> str:
        """Provide a detailed description of the radiation-affected tissue."""
        description = super().describe()
        radiation_info = [
            f"Radiation Level: {self.radiation_level:.2f}",
            f"Mutation Rate: {self.calculate_mutation_rate():.4f}",
            f"DNA Repair Rate: {self.dna_repair_rate:.2f}"
        ]
        return description + "\n" + "\n".join(radiation_info)

    def to_json(self) -> str:
        """Return a JSON representation of the radiation-affected tissue."""
        import json
        base_json = json.loads(super().to_json())
        base_json.update({
            "radiation_level": self.radiation_level,
            "mutation_rate": self.mutation_rate,
            "dna_repair_rate": self.dna_repair_rate
        })
        return json.dumps(base_json)

    @classmethod
    def from_json(cls, json_str: str) -> 'RadiationAffectedTissue':
        """Load a radiation-affected tissue from a JSON string."""
        import json
        tissue_dict = json.loads(json_str)
        cells = [Cell.from_json(json.dumps(cell_json)) for cell_json in tissue_dict['cells']]
        tissue = cls(
            name=tissue_dict['name'],
            tissue_type=tissue_dict['tissue_type'],
            cells=cells,
            cancer_risk=tissue_dict.get('cancer_risk', 0.005),
            radiation_level=tissue_dict.get('radiation_level', 0.0)
        )
        tissue.growth_rate = tissue_dict['growth_rate']
        tissue.healing_rate = tissue_dict['healing_rate']
        tissue.mutation_rate = tissue_dict.get('mutation_rate', 0.01)
        tissue.dna_repair_rate = tissue_dict.get('dna_repair_rate', 0.05)
        return tissue

    def visualize_tissue(self):
        """
        Create a 2D visual representation of the radiation-affected tissue.
        """
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import math

        fig, ax = plt.subplots(figsize=(10, 8))

        # Draw tissue boundary
        tissue_boundary = patches.Circle((0.5, 0.5), 0.45, edgecolor='black', facecolor='none', linewidth=2)
        ax.add_patch(tissue_boundary)

        # Draw cells
        num_cells = len(self.cells)
        for i, cell in enumerate(self.cells):
            angle = 2 * i * math.pi / num_cells
            x = 0.5 + 0.4 * math.cos(angle)
            y = 0.5 + 0.4 * math.sin(angle)

            # Color cells based on mutation status
            if cell.is_mutated:
                cell_color = 'red'
            else:
                cell_color = 'lightblue'

            cell_patch = patches.Circle((x, y), 0.05, edgecolor='blue', facecolor=cell_color, linewidth=1)
            ax.add_patch(cell_patch)
            ax.text(x, y, cell.name, fontsize=8, ha='center', va='center')

        # Display tissue name and type
        tissue_name_text = f"Tissue Name: {self.name}"
        tissue_type_text = f"Tissue Type: {self.tissue_type}"
        ax.text(0.1, 0.95, tissue_name_text, fontsize=12, ha='left', va='top', color='gray')
        ax.text(0.1, 0.90, tissue_type_text, fontsize=12, ha='left', va='top', color='gray')

        # Display radiation-specific information
        radiation_text = f"Radiation Level: {self.radiation_level:.2f}"
        mutation_rate_text = f"Mutation Rate: {self.calculate_mutation_rate():.4f}"
        ax.text(0.1, 0.85, radiation_text, fontsize=12, ha='left', va='top', color='red')
        ax.text(0.1, 0.80, mutation_rate_text, fontsize=12, ha='left', va='top', color='purple')

        # Display average cell health
        avg_health_text = f"Average Cell Health: {self.get_average_cell_health():.2f}"
        ax.text(0.9, 0.95, avg_health_text, fontsize=12, ha='right', va='top', color='blue')

        # Set plot limits and title
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.set_title(f"Radiation-Affected Tissue: {self.name}")
        ax.axis('off')

        plt.show()

    def get_state(self):
        """Return the state of the radiation-affected tissue as a tuple."""
        base_state = super().get_state()
        return base_state + (self.radiation_level, self.mutation_rate, self.dna_repair_rate)

    def __str__(self) -> str:
        """Return a string representation of the radiation-affected tissue."""
        return self.describe()
