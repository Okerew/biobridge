import random
from typing import List, Optional
from enum import Enum
from biobridge.blocks.cell import Cell


class InfectionType(Enum):
    PARASITE = "parasite"
    BACTERIA = "bacteria"
    VIRUS = "virus"


class Infection:
    def __init__(self, name: str, infection_type: InfectionType, spread_rate: float, genetic_code: str):
        """
        Initialize a new Infection object.

        :param name: Name of the infection
        :param infection_type: Type of infection (parasite, bacteria, or virus)
        :param spread_rate: Rate at which the infection spreads (0.0 to 1.0)
        :param genetic_code: Genetic code of the infection
        """
        self.name = name
        self.infection_type = infection_type
        self.spread_rate = max(0.0, min(1.0, spread_rate))  # Ensure spread_rate is between 0 and 1
        self.genetic_code = genetic_code
        self.infected_cells: List[str] = []  # List to store names of infected cells

    def infect(self, cell: 'Cell') -> bool:
        """
        Attempt to infect a cell.

        :param cell: The cell to attempt to infect
        :return: True if infection is successful, False otherwise
        """
        if random.random() < self.spread_rate:
            self.infected_cells.append(cell.name)
            return True
        return False

    def replicate(self, cell: 'Cell') -> None:
        """
        Replicate within an infected cell.

        :param cell: The infected cell
        """
        if cell.name in self.infected_cells:
            if cell.health is not None:  # Add this check
                # Simulate replication by decreasing cell health
                cell.health -= random.uniform(5, 15)
                cell.health = max(0, cell.health)  # Ensure health doesn't go below 0
            else:
                print("Error: cell.health is None")  # You can add some error handling here

    def exit_cell(self, cell: 'Cell') -> Optional['Infection']:
        """
        Attempt to exit the cell, potentially creating a new infection instance.

        :param cell: The infected cell
        :return: A new Infection instance if exit is successful, None otherwise
        """
        if cell.name in self.infected_cells:
            rand_value = random.random()
            print(f"Random value: {rand_value}, Spread rate: {self.spread_rate}")
            if rand_value < self.spread_rate:  # Use spread_rate for exit chance
                self.infected_cells.remove(cell.name)
                return Infection(f"{self.name}_offspring", self.infection_type, self.spread_rate, self.genetic_code)
        return None


    def mutate(self) -> None:
        """Simulate a random mutation in the infection."""
        mutation_type = random.choice(["spread_rate", "genetic_code"])

        if mutation_type == "spread_rate":
            self.spread_rate *= random.uniform(0.8, 1.2)
            self.spread_rate = max(0.0, min(1.0, self.spread_rate))  # Ensure spread_rate stays between 0 and 1
        else:  # genetic_code
            mutation_point = random.randint(0, len(self.genetic_code) - 1)
            new_base = random.choice("ATCG")
            self.genetic_code = self.genetic_code[:mutation_point] + new_base + self.genetic_code[mutation_point + 1:]

    def describe(self) -> str:
        """Provide a detailed description of the infection."""
        return f"""
Infection Name: {self.name}
Type: {self.infection_type.value}
Spread Rate: {self.spread_rate:.2f}
Genetic Code: {self.genetic_code}
Infected Cells: {len(self.infected_cells)}
        """.strip()

    def __str__(self) -> str:
        """Return a string representation of the infection."""
        return self.describe()
