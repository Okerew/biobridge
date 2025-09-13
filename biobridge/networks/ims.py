import random
from abc import ABC, abstractmethod
from typing import Any, List, Tuple

import matplotlib.pyplot as plt


class ImmuneCell(ABC):
    def __init__(self, name: str, strength: float, py_cell: Any):
        self.name = name
        self.strength = strength
        self.py_cell = py_cell
        self.activated = False

    @abstractmethod
    def attack(self, infection: Any) -> None:
        pass

    @abstractmethod
    def getType(self) -> str:
        pass

    def activate(self) -> None:
        if not self.activated:
            self.activated = True
            print(f"{self.getType()} {self.name} is activated.")
            self.strength *= 1.5
            self.py_cell.activated = True

    def deactivate(self) -> None:
        if self.activated:
            self.activated = False
            print(f"{self.getType()} {self.name} is deactivated.")
            self.strength /= 1.5
            self.py_cell.activated = False

    def getName(self) -> str:
        return self.name

    def getStrength(self) -> float:
        return self.strength

    def getPyCell(self) -> Any:
        return self.py_cell

    def isActivated(self) -> bool:
        return self.activated


class Macrophage(ImmuneCell):
    def attack(self, infection: Any) -> None:
        print(f"Macrophage {self.name} is engulfing the infection.")
        current_spread_rate = infection.spread_rate
        reduction_factor = 0.15 if self.activated else 0.1
        infection.spread_rate = max(
            0.0, current_spread_rate - reduction_factor * self.strength
        )
        health_reduction = 3 if self.activated else 5
        self.py_cell.health -= health_reduction

    def getType(self) -> str:
        return "Macrophage"

    def activate(self) -> None:
        super().activate()
        if self.activated:
            print(f"Macrophage {self.name} is releasing cytokines.")
            self.py_cell.add_surface_protein("MHC-II")

    def deactivate(self) -> None:
        super().deactivate()
        if not self.activated:
            print(f"Macrophage {self.name} has stopped releasing cytokines.")
            self.py_cell.remove_surface_protein("MHC-II")


class TCell(ImmuneCell):
    def attack(self, infection: Any) -> None:
        print(f"T Cell {self.name} is attacking infected cells.")
        infected_cells = infection.infected_cells
        cells_to_remove = int(self.strength * (3 if self.activated else 2))
        for _ in range(min(cells_to_remove, len(infected_cells))):
            if infected_cells:
                infected_cells.pop()
        health_reduction = 2 if self.activated else 3
        self.py_cell.health -= health_reduction

    def getType(self) -> str:
        return "T Cell"

    def activate(self) -> None:
        super().activate()
        if self.activated:
            print(f"T Cell {self.name} is producing cytokines.")
            self.py_cell.add_surface_protein("CD28")

    def deactivate(self) -> None:
        super().deactivate()
        if not self.activated:
            print(f"T Cell {self.name} has stopped producing cytokines.")
            self.py_cell.remove_surface_protein("CD28")


class BCell(ImmuneCell):
    def attack(self, infection: Any) -> None:
        print(f"B Cell {self.name} is producing antibodies.")
        current_spread_rate = infection.spread_rate
        reduction_factor = 0.08 if self.activated else 0.05
        infection.spread_rate = max(
            0.0, current_spread_rate - reduction_factor * self.strength
        )
        health_reduction = 1 if self.activated else 2
        self.py_cell.health -= health_reduction

    def getType(self) -> str:
        return "B Cell"

    def activate(self) -> None:
        super().activate()
        if self.activated:
            print(f"B Cell {self.name} is differentiating into plasma cells.")
            self.py_cell.add_surface_protein("CD19")

    def deactivate(self) -> None:
        super().deactivate()
        if not self.activated:
            print(f"B Cell {self.name} has stopped differentiating into plasma cells.")
            self.py_cell.remove_surface_protein("CD19")


class ImmuneSystem:
    def __init__(self, cell_class: Any, cells: List[Tuple[str, float, str]]):
        self.cell_class = cell_class
        self.immune_cells = cells
        self.cells: List[ImmuneCell] = []

        self.fig, self.ax = plt.subplots()
        self.createImmuneCells()

    def createImmuneCells(self) -> None:
        for cell in self.immune_cells:
            name, strength, type_ = cell
            py_cell = self.cell_class(name, type_, [], [], {})
            if type_ == "Macrophage":
                self.cells.append(Macrophage(name, strength, py_cell))
            elif type_ == "TCell":
                self.cells.append(TCell(name, strength, py_cell))
            elif type_ == "BCell":
                self.cells.append(BCell(name, strength, py_cell))

    def respond(self, infection: Any, cells: List[Any]) -> None:
        print("Immune system responding to infection:")
        totalATPProduced = 0.0
        try:
            allCells = cells.copy()
            for cell in self.cells:
                allCells.append(cell.getPyCell())

            for cell in allCells:
                if hasattr(cell, "getName"):
                    name = cell.getName() if hasattr(cell, "getName") else "Unknown"
                    print(f"Processing cell: {name}")
                if hasattr(infection, "infect"):
                    result = infection.infect(cell)
                    if isinstance(result, float):
                        print(
                            f"Cell {getattr(cell, 'name', 'Unknown')} infection result (float): {result}"
                        )
                    elif isinstance(result, bool):
                        print(
                            f"Cell {getattr(cell, 'name', 'Unknown')} was {'successfully infected' if result else 'not infected'}."
                        )
                    else:
                        raise RuntimeError("Error: Unexpected result type.")

            for immuneCell in self.cells:
                immuneCell.attack(infection)
                immuneCell.activate()

            if len(cells) < 10:
                try:
                    new_cell = cells[0].divide()
                    if new_cell is not None:
                        self.cells.append(
                            TCell(f"TCell{len(cells) + 1}", 0.8, new_cell)
                        )
                    else:
                        print("Error: Failed to create new cell.")
                except AttributeError as e:
                    print(f"Python error during cell division: {e}")

            for cell in allCells:
                if hasattr(cell, "getATPProduction"):
                    atpProduced = cell.getATPProduction()
                    totalATPProduced += atpProduced
                    print(
                        f"Cell {getattr(cell, 'name', 'Unknown')} produced {atpProduced} ATP."
                    )

            for immuneCell in self.cells:
                self.updateImmuneCell(immuneCell)

            print(f"Total ATP produced: {totalATPProduced}")
        except Exception as e:
            print(f"Exception occurred: {e}")

    def updateImmuneCell(self, cell: ImmuneCell) -> None:
        py_cell = cell.getPyCell()
        py_cell.metabolize()
        py_cell.update_structural_integrity()
        if py_cell.health <= 0:
            self.cells.remove(cell)

    def visualize(self, infection: Any, cells: List[Any]) -> None:
        self.ax.clear()
        spread_rate = infection.spread_rate
        self.ax.scatter(
            0, 0, s=spread_rate * 1000, c="red", alpha=0.5, label="Infection"
        )

        x, y, colors, sizes = [], [], [], []
        for cell in cells:
            x.append(random.uniform(-5, 5))
            y.append(random.uniform(-5, 5))
            cell_type = cell.cell_type if hasattr(cell, "cell_type") else "Unknown"
            if cell_type == "Macrophage":
                colors.append("blue")
            elif cell_type == "TCell":
                colors.append("green")
            elif cell_type == "BCell":
                colors.append("yellow")
            else:
                colors.append("gray")
            sizes.append(cell.health * 10)

        self.ax.scatter(x, y, c=colors, s=sizes, alpha=0.7)
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.set_title("Immune System Simulation")
        self.ax.legend()
        plt.draw()
        plt.pause(0.001)

    def getCells(self) -> List[Any]:
        return [cell.getPyCell() for cell in self.cells]
