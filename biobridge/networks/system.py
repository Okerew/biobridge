import random
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from biobridge.blocks.cell import Cell
from biobridge.blocks.tissue import Tissue
from biobridge.definitions.organ import Organ


class System:
    def __init__(self, name: str):
        self.name = name
        self.tissues: List[Tissue] = []
        self.organs: List[Organ] = []
        self.individual_cells: List[Cell] = []
        self.adaptation_rate = 0.1
        self.stress_level = 0.0
        self.previous_cell_count = 0
        self.previous_tissue_count = 0
        self.state = np.random.rand(5)  # 5-dimensional state vector
        self.health = 1.0
        self.energy = 1.0
        self.beneficial_mutation_chance = 0.1

    def add_tissue(self, tissue: Tissue) -> None:
        """Add a tissue to the system."""
        self.tissues.append(tissue)

    def add_organ(self, organ):
        """Add an organ to the system."""
        self.organs.append(organ)

    def remove_tissue(self, tissue: Tissue) -> None:
        """Remove a tissue from the system."""
        if tissue in self.tissues:
            self.tissues.remove(tissue)

    def add_cell(self, cell: Cell) -> None:
        """Add an individual cell to the system."""
        self.individual_cells.append(cell)

    def remove_cell(self, cell: Cell) -> None:
        """Remove an individual cell from the system."""
        if cell in self.individual_cells:
            self.individual_cells.remove(cell)

    def get_tissue_count(self) -> int:
        """Return the number of tissues in the system."""
        return len(self.tissues)

    def get_total_cell_count(self) -> int:
        """Return the total number of cells across all tissues and individual cells."""
        return sum(tissue.get_cell_count() for tissue in self.tissues) + len(
            self.individual_cells
        )

    def get_average_system_health(self) -> float:
        """Calculate and return the average health across all tissues and individual cells."""
        total_health = sum(
            tissue.get_average_cell_health() * tissue.get_cell_count()
            for tissue in self.tissues
        )
        total_health += sum(cell.health for cell in self.individual_cells)
        total_cells = self.get_total_cell_count()
        return total_health / total_cells if total_cells > 0 else 0

    def calculate_growth_factor(self) -> float:
        """Calculate a growth factor based on system conditions."""
        cell_count = self.get_total_cell_count()
        tissue_count = self.get_tissue_count()

        cell_growth_rate = (cell_count - self.previous_cell_count) / max(
            1, self.previous_cell_count
        )
        tissue_growth_rate = (tissue_count - self.previous_tissue_count) / max(
            1, self.previous_tissue_count
        )

        growth_factor = (cell_growth_rate + tissue_growth_rate) / 2
        return growth_factor

    def update_adaptation_rate(self) -> None:
        """Update the adaptation rate based on system changes."""
        growth_factor = self.calculate_growth_factor()
        health_factor = self.get_average_system_health() / 100

        # Adjust adaptation rate based on growth and health
        self.adaptation_rate = max(
            0.05, min(0.2, self.adaptation_rate * (1 + growth_factor) * health_factor)
        )

    def simulate_time_step(
        self, external_factors: Optional[List[tuple]] = None
    ) -> None:
        """
        Simulate one time step for the entire system.

        :param external_factors: List of tuples (factor, intensity) to apply to all tissues and cells
        """
        self.previous_cell_count = self.get_total_cell_count()
        self.previous_tissue_count = self.get_tissue_count()

        for tissue in self.tissues:
            tissue.simulate_time_step(external_factors)

        for cell in self.individual_cells:
            cell.metabolize()
            if external_factors:
                for factor, intensity in external_factors:
                    if factor == "radiation":
                        cell.health -= intensity * 20
                    elif factor == "toxin":
                        cell.health -= intensity * 15
                    elif factor == "nutrient":
                        cell.health += intensity * 10
                    cell.health = max(0, min(100, cell.health))

        self.update_adaptation_rate()
        self.simulate_system_adaptation()
        self.regulate_mutations()

    def apply_system_wide_stress(self, stress_amount: float) -> None:
        """
        Apply stress to all tissues and individual cells in the system.

        :param stress_amount: The amount of stress to apply
        """
        self.stress_level += stress_amount
        for tissue in self.tissues:
            tissue.apply_stress(stress_amount)
        for cell in self.individual_cells:
            cell.health -= random.uniform(0, stress_amount)
            cell.health = max(0, cell.health)

    def simulate_system_adaptation(self) -> None:
        """Simulate the system's adaptation to current conditions."""
        system_health = self.get_average_system_health()
        stress_factor = max(0, int(1 - self.stress_level))

        for tissue in self.tissues:
            # Adjust growth rate
            if system_health < 50:
                tissue.growth_rate *= 1 + self.adaptation_rate
            else:
                tissue.growth_rate = max(
                    0.05, tissue.growth_rate * (1 - self.adaptation_rate / 2)
                )

            # Adjust healing rate
            tissue.healing_rate = max(
                0.1, tissue.healing_rate * (1 + self.adaptation_rate * stress_factor)
            )

            # Adjust cancer risk based on stress and health
            tissue.cancer_risk = max(
                0.0001,
                tissue.cancer_risk * (1 + self.stress_level / 10 - system_health / 200),
            )

        # Adapt individual cells
        for cell in self.individual_cells:
            if system_health < 50:
                cell.health *= 1 + self.adaptation_rate / 2
            else:
                cell.health = max(0, int(cell.health * (1 - self.adaptation_rate / 4)))
            cell.health = min(100, cell.health)

        # Reduce stress level over time
        self.stress_level = max(0, int(self.stress_level * 0.9))

    def get_system_status(self) -> str:
        """Provide a detailed status report of the system."""
        status = [
            f"System Name: {self.name}",
            f"Number of Tissues: {self.get_tissue_count()}",
            f"Total Cell Count: {self.get_total_cell_count()}",
            f"Individual Cells: {len(self.individual_cells)}",
            f"Average System Health: {self.get_average_system_health():.2f}",
            f"Current Adaptation Rate: {self.adaptation_rate:.4f}",
            f"Current Stress Level: {self.stress_level:.4f}",
            "\nTissue Details:",
        ]
        for tissue in self.tissues:
            status.append(f"\n{tissue.describe()}")
        status.append("\nIndividual Cell Health:")
        for i, cell in enumerate(self.individual_cells):
            status.append(f"Cell {i + 1}: {cell.health:.2f}")
        return "\n".join(status)

    def to_json(self) -> str:
        """Return a JSON representation of the system."""
        import json

        return json.dumps(
            {
                "name": self.name,
                "tissues": [tissue.to_json() for tissue in self.tissues],
                "individual_cells": [cell.to_json() for cell in self.individual_cells],
                "adaptation_rate": self.adaptation_rate,
                "stress_level": self.stress_level,
                "previous_cell_count": self.previous_cell_count,
                "previous_tissue_count": self.previous_tissue_count,
            }
        )

    @classmethod
    def from_json(cls, json_str: str) -> "System":
        """Load a system from a JSON string."""
        import json

        system_dict = json.loads(json_str)
        system = cls(name=system_dict["name"])
        for tissue_json in system_dict["tissues"]:
            system.add_tissue(Tissue.from_json(tissue_json))
        for cell_json in system_dict["individual_cells"]:
            system.add_cell(Cell.from_json(cell_json))
        system.adaptation_rate = system_dict["adaptation_rate"]
        system.stress_level = system_dict["stress_level"]
        system.previous_cell_count = system_dict["previous_cell_count"]
        system.previous_tissue_count = system_dict["previous_tissue_count"]
        return system

    def update(self, network_output: Dict[str, float]):
        # Update system based on neural network output
        for key, value in network_output.items():
            if key.startswith(f"{self.name}_"):
                action = key.split("_")[1]
                if action == "move":
                    self.state += np.random.normal(0, value, 5)
                elif action == "heal":
                    self.health = min(1.0, self.health + value * 0.1)
                elif action == "energize":
                    self.energy = min(1.0, self.energy + value * 0.1)

        # Natural decay
        self.health -= 0.01
        self.energy -= 0.02
        self.health = max(0, min(1, int(self.health)))
        self.energy = max(0, min(1, int(self.energy)))

    def get_status(self) -> float:
        return (self.health + self.energy) / 2

    def visualize_network(self):
        G = nx.DiGraph()

        for tissue in self.tissues:
            G.add_node(tissue.name, color="red")

        pos = nx.spring_layout(G)
        plt.figure(figsize=(12, 8))

        nx.draw_networkx_nodes(
            G, pos, node_color=[G.nodes[n]["color"] for n in G.nodes]
        )
        nx.draw_networkx_labels(G, pos)

        edge_weights = nx.get_edge_attributes(G, "weight")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_weights)

        plt.title("System")
        plt.axis("off")
        plt.show()

    def regulate_mutations(self) -> None:
        """
        Regulate mutations in the system, allowing only potentially beneficial ones to persist.
        This function simulates the biological process of mutation and selection.
        """
        for tissue in self.tissues:
            for cell in tissue.cells:
                if random.random() < self.mutation_rate:
                    # A mutation has occurred
                    if random.random() < self.beneficial_mutation_chance:
                        # Potentially beneficial mutation
                        benefit = random.uniform(0, 0.1)  # Small random benefit

                        # Apply the benefit to a random attribute
                        attribute = random.choice(["health", "energy", "growth_rate"])
                        if attribute == "health":
                            cell.health = min(100, cell.health + benefit * 100)
                        elif attribute == "energy":
                            cell.energy += benefit
                        elif attribute == "growth_rate":
                            cell.growth_rate += benefit

                        print(
                            f"Potentially beneficial mutation occurred in {tissue.name}, cell {cell.id}"
                        )
                    else:
                        # Non-beneficial mutation, it will be "repaired" or the cell will be eliminated
                        if random.random() < 0.5:  # 50% chance of successful repair
                            print(
                                f"Non-beneficial mutation repaired in {tissue.name}, cell {cell.id}"
                            )
                        else:
                            tissue.remove_cell(cell)
                            print(
                                f"Cell with non-beneficial mutation eliminated from {tissue.name}"
                            )

        # Also regulate mutations in individual cells
        for cell in self.individual_cells:
            if random.random() < self.mutation_rate:
                if random.random() < self.beneficial_mutation_chance:
                    benefit = random.uniform(0, 0.1)
                    attribute = random.choice(["health", "energy"])
                    if attribute == "health":
                        cell.health = min(100, int(cell.health + benefit * 100))
                    elif attribute == "energy":
                        self.energy += benefit
                    print(
                        f"Potentially beneficial mutation occurred in individual cell {cell.id}"
                    )
                else:
                    if random.random() < 0.5:
                        print(
                            f"Non-beneficial mutation repaired in individual cell {cell.id}"
                        )
                    else:
                        self.remove_cell(cell)
                        print(
                            f"Individual cell with non-beneficial mutation eliminated"
                        )

    def __str__(self) -> str:
        """Return a string representation of the system."""
        return self.get_system_status()

    def __getattr__(self, item):
        return self.__dict__.get(item)

    def __eq__(self, other):
        if isinstance(other, System):
            return self.name == other.name
        return False
