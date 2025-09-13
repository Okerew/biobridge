import random
from typing import List, Optional, Dict, Tuple, Callable, Any
from biobridge.blocks.cell import Cell
from biobridge.blocks.tissue import Tissue
import json
from biobridge.definitions.organism import Organism
from biobridge.definitions.ao import AdvancedOrganism


class Substance:
    def __init__(self, name: str, effect: Dict[str, float]):
        """
        Initialize a new Substance object.

        :param name: Name of the substance
        :param effect: Dictionary of effects on cells and tissues
        """
        self.name = name
        self.effect = effect

    def apply_effect(self, cell: "Cell", intensity: float) -> None:
        """Apply the substance effect to a cell."""
        for factor, impact in self.effect.items():
            if factor == "health":
                cell.health += impact * intensity
            # Add more factors as needed
            cell.health = max(0, min(100, cell.health))

    def __str__(self) -> str:
        """Return a string representation of the substance."""
        return f"Substance(name={self.name}, effect={self.effect})"


class Environment:
    def __init__(self, name: str, width: int, height: int, temperature: float, humidity: float,
                 env_type: str = "normal",
                 cells: Optional[List[Cell]] = None,
                 tissues: Optional[List[Tissue]] = None,
                 organisms: Optional[List[Organism]] = None,
                 advanced_organisms: Optional[List[AdvancedOrganism]] = None,
                 environmental_factors: Optional[Dict[str, float]] = None,
                 substances: Optional[Dict[str, Substance]] = None):
        """
        Initialize a new Environment object.

        :param name: Name of the environment
        :param width: Width of the environment
        :param height: Height of the environment
        :param temperature: Temperature of the environment in Celsius
        :param humidity: Humidity of the environment in percentage
        :param env_type: Type of environment ("normal" for air or "water")
        :param cells: List of Cell objects in the environment
        :param tissues: List of Tissue objects in the environment
        :param environmental_factors: Dictionary of environmental factors and their intensities
        :param substances: Dictionary of substances and their effects
        """
        self.name = name
        self.width = width
        self.height = height
        self.temperature = temperature
        self.humidity = humidity
        self.env_type = env_type.lower()
        if self.env_type not in ["normal", "water"]:
            raise ValueError("Environment type must be either 'normal' or 'water'")
        self.cells = {}  # Dictionary to store cells with their coordinates
        self.tissues = {}  # Dictionary to store tissues with their coordinates
        self.environmental_factors = environmental_factors or {}
        self.substances = substances or {}
        self.base_cancer_risk = 0.001  # Base cancer risk (0.1%)
        self.movement_hooks: List[Callable[[Tuple[int, int], Cell], Tuple[int, int]]] = []
        self.organisms = {}  # Dictionary to store organisms with their coordinates
        self.advanced_organisms = {}  # Dictionary to store advanced organisms with their coordinates
        self.comfortability_factor = 1.0  # Base comfortability factor

        # Initialize organisms with coordinates
        if organisms:
            for organism in organisms:
                self.add_organism(organism, self._get_random_position())

        # Initialize cells and tissues with coordinates
        if cells:
            for cell in cells:
                self.add_cell(cell, self._get_random_position())
        if tissues:
            for tissue in tissues:
                self.add_tissue(tissue, self._get_random_position())

        if advanced_organisms:
            for advanced_organism in advanced_organisms:
                self.add_advanced_organism(advanced_organism, self._get_random_position())

    def _get_random_position(self) -> Tuple[int, int]:
        """Get a random position within the environment's boundaries."""
        return random.randint(0, self.width - 1), random.randint(0, self.height - 1)

    def add_cell(self, cell: Cell, position: Tuple[int, int]) -> None:
        """Add a cell to the environment at the specified position."""
        if 0 <= position[0] < self.width and 0 <= position[1] < self.height:
            self.cells[position] = cell
        else:
            raise ValueError(f"Position {position} is outside the environment boundaries.")

    def remove_cell(self, position: Tuple[int, int]) -> None:
        """Remove a cell from the environment at the specified position."""
        self.cells.pop(position, None)

    def add_tissue(self, tissue: Tissue, position: Tuple[int, int]) -> None:
        """Add a tissue to the environment at the specified position."""
        if 0 <= position[0] < self.width and 0 <= position[1] < self.height:
            self.tissues[position] = tissue
        else:
            raise ValueError(f"Position {position} is outside the environment boundaries.")

    def remove_tissue(self, position: Tuple[int, int]) -> None:
        """Remove a tissue from the environment at the specified position."""
        self.tissues.pop(position, None)

    def calculate_cancer_risk(self) -> float:
        """Calculate the current cancer risk based on environmental factors."""
        risk = self.base_cancer_risk

        # Adjust risk based on temperature
        if self.temperature > 40 or self.temperature < 10:
            risk *= 1.5

        # Adjust risk based on environmental factors
        if "radiation" in self.environmental_factors:
            risk *= (1 + self.environmental_factors["radiation"] * 2)
        if "toxin" in self.environmental_factors:
            risk *= (1 + self.environmental_factors["toxin"])
        if "nutrient" in self.environmental_factors:
            risk /= (1 + self.environmental_factors["nutrient"] * 0.5)

        # Adjust risk based on drugs
        for substance in self.substances.values():
            if "cancer_risk" in substance.effect:
                risk *= (1 + substance.effect["cancer_risk"])

        return min(risk, 1.0)  # Ensure risk doesn't exceed 100%

    def add_organism(self, organism: Organism, position: Tuple[int, int]) -> None:
        """Add an organism to the environment at the specified position."""
        if 0 <= position[0] < self.width and 0 <= position[1] < self.height:
            self.organisms[position] = organism
        else:
            raise ValueError(f"Position {position} is outside the environment boundaries.")

    def remove_organism(self, position: Tuple[int, int]) -> None:
        """Remove an organism from the environment at the specified position."""
        self.organisms.pop(position, None)

    def add_advanced_organism(self, advanced_organism: AdvancedOrganism, position: Tuple[int, int]) -> None:
        """Add an advanced organism to the environment at the specified position."""
        if 0 <= position[0] < self.width and 0 <= position[1] < self.height:
            self.advanced_organisms[position] = advanced_organism
        else:
            raise ValueError(f"Position {position} is outside the environment boundaries.")

    def remove_advanced_organism(self, position: Tuple[int, int]) -> None:
        """Remove an advanced organism from the environment at the specified position."""
        self.advanced_organisms.pop(position, None)

    def get_neighbors(self, position: Tuple[int, int], radius: int = 1) -> List[Tuple[Tuple[int, int], Cell]]:
        """Get neighboring cells within a specified radius."""
        neighbors = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                new_pos = (position[0] + dx, position[1] + dy)
                if new_pos in self.cells:
                    neighbors.append((new_pos, self.cells[new_pos]))
        return neighbors

    def add_movement_hook(self, hook: Callable[[Tuple[int, int], Cell], Tuple[int, int]]) -> None:
        """Add a movement hook function to modify cell positions."""
        self.movement_hooks.append(hook)

    def apply_movement_hooks(self) -> None:
        """Apply all movement hooks to modify cell positions."""
        new_positions = {}
        for position, cell in self.cells.items():
            new_pos = position
            for hook in self.movement_hooks:
                new_pos = hook(new_pos, cell)
            new_pos = (
                max(0, min(self.width - 1, new_pos[0])),
                max(0, min(self.height - 1, new_pos[1]))
            )
            new_positions[new_pos] = cell

        self.cells = new_positions

    def calculate_comfortability(self) -> float:
        """Calculate the current comfortability factor based on environmental conditions."""
        comfort = self.comfortability_factor

        # Adjust comfort based on temperature
        optimal_temp = 25  # Assume 25°C is the optimal temperature
        temp_diff = abs(self.temperature - optimal_temp)
        comfort *= max(0, int(1 - (temp_diff / 50)))  # Reduce comfort as temperature deviates from optimal

        # Adjust comfort based on humidity
        optimal_humidity = 50  # Assume 50% is the optimal humidity
        humidity_diff = abs(self.humidity - optimal_humidity)
        comfort *= max(0, int(1 - (humidity_diff / 100)))

        # Adjust comfort based on environmental factors
        for factor, intensity in self.environmental_factors.items():
            if factor == "toxin":
                comfort *= max(0, int(1 - (intensity * 0.5)))
            elif factor == "nutrient":
                comfort *= min(2, int(1 + (intensity * 0.2)))

        return max(0, min(comfort, 2))  # Ensure comfort is between 0 and 2

    def _find_partner(self, organism: Organism) -> Optional[Organism]:
        """Find a suitable partner for reproduction among nearby organisms."""
        nearby_organisms = [org for pos, org in self.organisms.items() if org != organism and org.get_health() > 50]
        return random.choice(nearby_organisms) if nearby_organisms else None

    def _find_advanced_partner(self, advanced_organism: AdvancedOrganism) -> Optional[AdvancedOrganism]:
        """Find a suitable partner for reproduction among nearby advanced organisms."""
        nearby_advanced_organisms = [org for pos, org in self.advanced_organisms.items() if org != advanced_organism and org.get_health() > 50]
        return random.choice(nearby_advanced_organisms) if nearby_advanced_organisms else None

    def remove_dead_organisms(self) -> None:
        """Remove organisms with zero health from the environment."""
        self.organisms = {pos: org for pos, org in self.organisms.items() if org.get_health() > 0}
        self.advanced_organisms = {pos: org for pos, org in self.advanced_organisms.items() if org.get_health() > 0}

    def simulate_time_step(self) -> None:
        """Simulate one time step in the environment's life, including environmental factors, cell movement, and organism actions."""
        current_comfort = self.calculate_comfortability()

        # Cell and tissue simulation
        new_cells = {}
        for position, cell in self.cells.items():
            cell.metabolize()
            if cell.health > 70 and random.random() < 0.1 * current_comfort:  # Increased chance of division when comfortable
                new_cell = cell.divide()
                new_position = self._get_random_position()
                new_cells[new_position] = new_cell

        self.cells.update(new_cells)

        for position, tissue in self.tissues.items():
            tissue.simulate_time_step(list(self.environmental_factors.items()))

        # Organism simulation
        new_organisms = {}
        for position, organism in self.organisms.items():
            organism.update(list(self.environmental_factors.items()))
            if organism.get_health() > 70 and random.random() < 0.05 * current_comfort:  # Chance of reproduction when comfortable
                partner = self._find_partner(organism)
                if partner:
                    new_organism = organism.reproduce(partner)
                    new_position = self._get_random_position()
                    new_organisms[new_position] = new_organism

        self.organisms.update(new_organisms)

        # Advanced Organism simulation
        new_advanced_organisms = {}
        for position, advanced_organism in self.advanced_organisms.items():
            advanced_organism.update(list(self.environmental_factors.items()))
            if advanced_organism.get_health() > 70 and random.random() < 0.05 * current_comfort:  # Chance of reproduction when comfortable
                partner = self._find_advanced_partner(advanced_organism)
                if partner:
                    new_advanced_organism = advanced_organism.reproduce(partner)
                    new_position = self._get_random_position()
                    new_advanced_organisms[new_position] = new_advanced_organism

        self.advanced_organisms.update(new_advanced_organisms)

        self.apply_environmental_factors()
        self.apply_movement_hooks()
        self.remove_dead_cells()
        self.remove_dead_organisms()

    def apply_environmental_factors(self) -> None:
        """Apply environmental factors to all cells and tissues in the environment."""
        current_cancer_risk = self.calculate_cancer_risk()
        current_comfort = self.calculate_comfortability()

        for position, cell in self.cells.items():
            for factor, intensity in self.environmental_factors.items():
                if factor == "radiation":
                    cell.health -= intensity * 20
                elif factor == "toxin":
                    cell.health -= intensity * 15
                elif factor == "nutrient":
                    cell.health += intensity * 10
                cell.health = max(0, min(100, cell.health))

            for substance_name, substance in self.substances.items():
                substance.apply_effect(cell, self.environmental_factors.get(substance_name, 0))

            # Apply cancer risk
            if random.random() < current_cancer_risk:
                cell.mutate()  # Assume Cell class has a mutate method to represent cancerous changes

        for position, tissue in self.tissues.items():
            for factor, intensity in self.environmental_factors.items():
                tissue.apply_external_factor(factor, intensity)

            # Update tissue's cancer risk
            tissue.cancer_risk = current_cancer_risk

        for position, organism in self.organisms.items():
            for factor, intensity in self.environmental_factors.items():
                if factor == "radiation":
                    organism.health -= intensity * 15
                elif factor == "toxin":
                    organism.health -= intensity * 10
                elif factor == "nutrient":
                    organism.health += intensity * 5
                organism.health = max(0, min(100, organism.health))

            for substance_name, substance in self.substances.items():
                substance.apply_effect(organism, self.environmental_factors.get(substance_name, 0))

            # Apply comfort factor to organism
            organism.energy += (
                                           current_comfort - 1) * 5  # Increase energy when comfortable, decrease when uncomfortable
            organism.energy = max(0, min(100, organism.energy))

        for position, advanced_organism in self.advanced_organisms.items():
            for factor, intensity in self.environmental_factors.items():
                if factor == "radiation":
                    advanced_organism.health -= intensity * 15
                elif factor == "toxin":
                    advanced_organism.health -= intensity * 10
                elif factor == "nutrient":
                    advanced_organism.health += intensity * 5
                advanced_organism.health = max(0, min(100, advanced_organism.health))

            for substance_name, substance in self.substances.items():
                substance.apply_effect(advanced_organism, self.environmental_factors.get(substance_name, 0))

            # Apply comfort factor to advanced_organism
            advanced_organism.energy += (
                                           current_comfort - 1) * 5  # Increase energy when comfortable, decrease when uncomfortable
            advanced_organism.energy = max(0, min(100, advanced_organism.energy))

    def remove_dead_cells(self) -> None:
        """Remove cells with zero health from the environment."""
        self.cells = {pos: cell for pos, cell in self.cells.items() if cell.health > 0}

    def describe(self) -> str:
        """Provide a detailed description of the environment."""
        description = [
            f"Environment Name: {self.name}",
            f"Environment Type: {'Water' if self.env_type == 'water' else 'Normal (Air)'}",
            f"Dimensions: {self.width}x{self.height}",
            f"Temperature: {self.temperature}°C",
            f"Humidity: {self.humidity}%",
            f"Comfortability Factor: {self.calculate_comfortability():.2f}",
            f"Number of Cells: {len(self.cells)}",
            f"Number of Tissues: {len(self.tissues)}",
            f"Number of Organisms: {len(self.organisms)}",
            f"Number of Advanced Organisms: {len(self.advanced_organisms)}",
            f"Current Cancer Risk: {self.calculate_cancer_risk():.4%}",
            "Environmental Factors:",
        ]
        for factor, intensity in self.environmental_factors.items():
            description.append(f"  {factor}: {intensity}")

        if self.cells:
            description.append("\nCells:")
            for position, cell in self.cells.items():
                description.append(f"  Position {position}: {cell.describe()}")
        else:
            description.append("No cells present.")

        if self.tissues:
            description.append("\nTissues:")
            for position, tissue in self.tissues.items():
                description.append(f"  Position {position}: {tissue.describe()}")
        else:
            description.append("No tissues present.")

        if self.organisms:
            description.append("\nOrganisms:")
            for position, organism in self.organisms.items():
                description.append(f"  Position {position}: {organism.describe()}")
        else:
            description.append("No organisms present.")

        if self.advanced_organisms:
            description.append("\nAdvanced Organisms:")
            for position, advanced_organism in self.advanced_organisms.items():
                description.append(f"  Position {position}: {advanced_organism.describe()}")
        else:
            description.append("No advanced organisms present.")

        return "\n".join(description)

    def to_json(self) -> str:
        """Return a JSON representation of the environment."""
        return json.dumps({
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "env_type": self.env_type,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "cells": {str(pos): cell.to_json() for pos, cell in self.cells.items()},
            "tissues": {str(pos): tissue.to_json() for pos, tissue in self.tissues.items()},
            "organisms": {str(pos): organism.to_json() for pos, organism in self.organisms.items()},
            "advanced_organisms": {str(pos): advanced_organism.to_json() for pos, advanced_organism in
                                   self.advanced_organisms.items()},
            "environmental_factors": self.environmental_factors,
            "substances": {name: substance.effect for name, substance in self.substances.items()},
            "base_cancer_risk": self.base_cancer_risk,
            "comfortability_factor": self.comfortability_factor
        })

    @classmethod
    def from_json(cls, json_str: str) -> 'Environment':
        """Load an environment from a JSON string."""
        env_dict = json.loads(json_str)
        cells = {eval(pos): Cell.from_json(cell_json) for pos, cell_json in env_dict['cells'].items()}
        tissues = {eval(pos): Tissue.from_json(tissue_json) for pos, tissue_json in env_dict['tissues'].items()}
        organisms = {eval(pos): Organism.from_json(org_json) for pos, org_json in env_dict['organisms'].items()}
        advanced_organisms = {eval(pos): AdvancedOrganism.from_json(org_json) for pos, org_json in
                              env_dict['advanced_organisms'].items()}
        substances = {name: Substance(name, effect) for name, effect in env_dict['substances'].items()}
        environment = cls(
            name=env_dict['name'],
            width=env_dict['width'],
            height=env_dict['height'],
            temperature=env_dict['temperature'],
            humidity=env_dict['humidity'],
            env_type=env_dict['env_type'],
            environmental_factors=env_dict['environmental_factors'],
            substances=substances
        )
        environment.cells = cells
        environment.tissues = tissues
        environment.organisms = organisms
        environment.base_cancer_risk = env_dict['base_cancer_risk']
        environment.comfortability_factor = env_dict['comfortability_factor']
        return environment

    def get_cell_positions(self) -> List[Dict[str, Any]]:
        return [
            {
                "x": pos[0],
                "y": pos[1],
                "health": cell.health,
                "type": cell.__class__.__name__,
                "id": id(cell)
            }
            for pos, cell in self.cells.items()
        ]

    def get_tissue_positions(self) -> List[Dict[str, Any]]:
        return [
            {
                "x": pos[0],
                "y": pos[1],
                "health": tissue.health,
                "type": tissue.__class__.__name__,
                "id": id(tissue)
            }
            for pos, tissue in self.tissues.items()
        ]

    def get_organism_positions(self) -> List[Dict[str, Any]]:
        return [
            {
                "x": pos[0],
                "y": pos[1],
                "health": organism.health,
                "type": organism.__class__.__name__,
                "id": id(organism)
            }
            for pos, organism in self.organisms.items()
        ]

    def get_advanced_organism_positions(self) -> List[Dict[str, Any]]:
        return [
            {
                "x": pos[0],
                "y": pos[1],
                "health": advanced_organism.health,
                "type": advanced_organism.__class__.__name__,
                "id": id(advanced_organism)
            }
            for pos, advanced_organism in self.advanced_organisms.items()
        ]

    def move_cell(self, cell_id: int, new_x: int, new_y: int) -> None:
        for pos, cell in list(self.cells.items()):
            if id(cell) == cell_id:
                old_pos = pos
                new_pos = (new_x, new_y)
                if new_pos in self.cells:
                    return  # Don't move if position is occupied
                self.cells[new_pos] = cell
                del self.cells[old_pos]
                break

    def move_tissue(self, tissue_id: int, new_x: int, new_y: int) -> None:
        for pos, tissue in list(self.tissues.items()):
            if id(tissue) == tissue_id:
                old_pos = pos
                new_pos = (new_x, new_y)
                if new_pos in self.tissues:
                    return  # Don't move if position is occupied
                self.tissues[new_pos] = tissue
                del self.tissues[old_pos]
                break

    def move_organism(self, org_id: int, new_x: int, new_y: int) -> None:
        for pos, org in list(self.organisms.items()):
            if id(org) == org_id:
                old_pos = pos
                new_pos = (new_x, new_y)
                if new_pos in self.organisms:
                    return  # Don't move if position is occupied
                self.organisms[new_pos] = org
                del self.organisms[old_pos]
                break

    def move_advanced_organism(self, org_id: int, new_x: int, new_y: int) -> None:
        for pos, org in list(self.advanced_organisms.items()):
            if id(org) == org_id:
                old_pos = pos
                new_pos = (new_x, new_y)
                if new_pos in self.advanced_organisms:
                    return  # Don't move if position is occupied
                self.advanced_organisms[new_pos] = org
                del self.advanced_organisms[old_pos]
                break

    def __str__(self) -> str:
        """Return a string representation of the environment."""
        return self.describe()
