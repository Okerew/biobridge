import random
from typing import List, Optional
from biobridge.blocks.cell import Cell, math, plt, patches


class Tissue:
    def __init__(self, name: str, tissue_type: str, cells: Optional[List[Cell]] = None, cancer_risk: float = 0.001, mutation_rate: float = 0.05):
        self.name = name
        self.tissue_type = tissue_type
        self.cells = cells or []
        self.growth_rate = 0.05
        self.healing_rate = 0.1
        self.cancer_risk = cancer_risk
        self.mutation_rate = mutation_rate
        self.mutation_threshold = 3

    def add_cell(self, cell: Cell) -> None:
        """Add a cell to the tissue."""
        self.cells.append(cell)

    def remove_cell(self, cell: Cell) -> None:
        """Remove a cell from the tissue."""
        if cell in self.cells:
            self.cells.remove(cell)

    def mutate(self):
        """Simulate mutations in the tissue."""
        for cell in self.cells:
            cell.mutate()

    def get_cell_count(self) -> int:
        """Return the number of cells in the tissue."""
        return len(self.cells)

    def get_average_cell_health(self) -> float:
        """Calculate and return the average health of all cells in the tissue."""
        if not self.cells:
            return 0
        return sum(cell.health for cell in self.cells) / len(self.cells)

    def tissue_metabolism(self) -> None:
        """Simulate the metabolism of all cells in the tissue."""
        for cell in self.cells:
            cell.metabolize()

    def tissue_repair(self, amount: float) -> None:
        """
        Repair all cells in the tissue.

        :param amount: The amount of health to restore to each cell
        """
        for cell in self.cells:
            cell.repair(amount)

    def simulate_cell_division(self) -> None:
        """Simulate cell division in the tissue, including regulated mutations."""
        new_cells = []
        for cell in self.cells:
            if cell.health > 70 and random.random() < 0.1:  # 10% chance of division for healthy cells
                new_cell = cell.divide()

                # Apply mutations based on mutation rate
                if random.random() < self.mutation_rate:
                    mutation_count = self.apply_mutation(new_cell)

                    # Check if the cell has become cancerous
                    if mutation_count >= self.mutation_threshold:
                        new_cell.is_cancerous = True

                new_cells.append(new_cell)

        self.cells.extend(new_cells)

    def apply_mutation(self, cell: Cell) -> int:
        """
        Apply a mutation to a cell and return the total mutation count.

        :param cell: The cell to mutate
        :return: The total number of mutations in the cell
        """
        mutation_type = random.choice(["growth", "repair", "metabolism"])

        if mutation_type == "growth":
            cell.growth_rate *= random.uniform(0.9, 1.1)  # 10% change in growth rate
        elif mutation_type == "repair":
            cell.repair_rate *= random.uniform(0.9, 1.1)  # 10% change in repair rate
        elif mutation_type == "metabolism":
            cell.metabolism_rate *= random.uniform(0.9, 1.1)  # 10% change in metabolism rate

        cell.mutation_count += 1
        return cell.mutation_count

    def simulate_time_step(self, external_factors: List[tuple] = None) -> None:
        """
        Simulate one time step in the tissue's life, including growth, healing, mutations, and external factors.

        :param external_factors: List of tuples (factor, intensity) to apply
        """
        self.tissue_metabolism()
        self.simulate_growth()
        self.simulate_cell_division()
        self.remove_dead_cells()

        if external_factors:
            for factor, intensity in external_factors:
                self.apply_external_factor(factor, intensity)

        # Modified wound simulation
        if random.random() < 0.1:  # 10% chance of wound occurring
            cell_count = self.get_cell_count()
            if cell_count > 1:
                max_wound_size = max(1, int(cell_count * 0.1))
                wound_size = random.randint(1, max_wound_size)
                self.simulate_wound_healing(wound_size)
            else:
                print(f"Warning: Not enough cells in {self.name} to simulate wound healing.")

    def apply_stress(self, stress_amount: float) -> None:
        """
        Apply stress to the tissue, potentially damaging cells.

        :param stress_amount: The amount of stress to apply
        """
        for cell in self.cells:
            cell.health -= random.uniform(0, stress_amount)
            cell.health = max(0, cell.health)

    def remove_dead_cells(self) -> None:
        """Remove cells with zero health from the tissue."""
        self.cells = [cell for cell in self.cells if cell.health > 0]

    def simulate_growth(self) -> None:
        """Simulate tissue growth by adding new cells."""
        new_cells_count = int(self.get_cell_count() * self.growth_rate)
        for _ in range(new_cells_count):
            new_cell = Cell(f"Cell_{random.randint(1000, 9999)}", str(random.uniform(80, 100)))
            self.add_cell(new_cell)

    def simulate_wound_healing(self, wound_size: int) -> None:
        """
        Simulate wound healing by regenerating cells.

        :param wound_size: The number of cells destroyed by the wound
        """
        self.cells = self.cells[:-wound_size]  # Remove wounded cells
        healing_cells = int(wound_size * self.healing_rate)
        for _ in range(healing_cells):
            new_cell = Cell(f"Cell_{random.randint(1000, 9999)}", str(random.uniform(60, 80)))
            self.add_cell(new_cell)

    def apply_external_factor(self, factor: str, intensity: float) -> None:
        """
        Apply an external factor to the tissue, affecting cell health.

        :param factor: The type of external factor (e.g., "radiation", "toxin", "nutrient")
        :param intensity: The intensity of the factor (0 to 1)
        """
        for cell in self.cells:
            if factor == "radiation":
                cell.health -= intensity * 20
            elif factor == "toxin":
                cell.health -= intensity * 15
            elif factor == "nutrient":
                cell.health += intensity * 10
            cell.health = max(0, min(100, cell.health))

    def describe(self) -> str:
        """Provide a detailed description of the tissue."""
        description = [
            f"Tissue Name: {self.name}",
            f"Tissue Type: {self.tissue_type}",
            f"Number of Cells: {self.get_cell_count()}",
            f"Average Cell Health: {self.get_average_cell_health():.2f}",
            f"Growth Rate: {self.growth_rate:.2%}",
            f"Healing Rate: {self.healing_rate:.2%}",
            f"Cancer Risk: {self.cancer_risk:.4%}"
        ]
        return "\n".join(description)

    def to_json(self) -> str:
        """Return a JSON representation of the tissue."""
        import json
        return json.dumps({
            "name": self.name,
            "tissue_type": self.tissue_type,
            "cells": [cell.to_json() for cell in self.cells],
            "growth_rate": self.growth_rate,
            "healing_rate": self.healing_rate,
            "cancer_risk": self.cancer_risk
        })

    @classmethod
    def from_json(cls, json_str: str) -> 'Tissue':
        """Load a tissue from a JSON string."""
        import json
        tissue_dict = json.loads(json_str)
        cells = [Cell.from_json(cell_json) for cell_json in tissue_dict['cells']]
        tissue = cls(
            name=tissue_dict['name'],
            tissue_type=tissue_dict['tissue_type'],
            cells=cells,
            cancer_risk=tissue_dict.get('cancer_risk', 0.001)  # Default to 0.001 if not provided
        )
        tissue.growth_rate = tissue_dict['growth_rate']
        tissue.healing_rate = tissue_dict['healing_rate']
        return tissue

    def visualize_tissue(self):
        """
        Create a 2D visual representation of the tissue.
        """
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
            cell_patch = patches.Circle((x, y), 0.05, edgecolor='blue', facecolor='lightblue', linewidth=1)
            ax.add_patch(cell_patch)
            ax.text(x, y, cell.name, fontsize=8, ha='center', va='center')

        # Display tissue name and type
        tissue_name_text = f"Tissue Name: {self.name}"
        tissue_type_text = f"Tissue Type: {self.tissue_type}"
        ax.text(0.1, 0.9, tissue_name_text, fontsize=12, ha='left', va='bottom', color='gray')
        ax.text(0.1, 0.85, tissue_type_text, fontsize=12, ha='left', va='bottom', color='gray')

        # Display average cell health
        avg_health_text = f"Average Cell Health: {self.get_average_cell_health():.2f}"
        ax.text(0.8, 0.9, avg_health_text, fontsize=12, ha='right', va='bottom', color='red')

        # Set plot limits and title
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.set_title(f"Tissue: {self.name}")
        ax.axis('off')

        plt.show()

    def get_state(self):
        """Return the state of the tissue as a tuple."""
        return self.name, self.tissue_type, self.cells, self.growth_rate, self.healing_rate, self.cancer_risk

    def calculate_molecular_weight(self, custom_weights: dict = None) -> float:
        """
        Calculate the molecular weight of the entire tissue.

        :param custom_weights: A dictionary of custom weights for different tissue components.
            The keys should be 'water', 'cell_membrane', 'organelles', and 'cell_volume'.
            The values should be the corresponding molecular weights in Daltons.
        :return: The total molecular weight of the tissue in Daltons.
        """
        default_weights = {
            'water': 1e12,  # 1 trillion Daltons
            'cell_membrane': 2e9,  # 2 billion Daltons
            'organelles': 5e11,  # 500 billion Daltons
            'cell_volume': 1e12,  # 1 trillion Daltons
        }

        weights = custom_weights or default_weights

        total_weight = 0
        for cell in self.cells:
            total_weight += cell.calculate_molecular_weight(weights)

        return total_weight

    def __str__(self) -> str:
        """Return a string representation of the tissue."""
        return self.describe()
