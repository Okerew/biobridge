import random
from typing import List, Optional

from biobridge.blocks.cell import Cell
from biobridge.blocks.tissue import Tissue


class BoneTissue(Tissue):
    def __init__(
        self,
        name: str,
        cells: Optional[List[Cell]] = None,
        cancer_risk: float = 0.001,
        mineral_density: float = 1.0,
    ):
        """
        Initialize a new BoneTissue object.

        :param name: Name of the bone tissue
        :param cells: List of Cell objects that make up the bone tissue
        :param cancer_risk: Risk of cancer in bone tissue
        :param mineral_density: The mineral density of the bone tissue (important for bone strength)
        """
        super().__init__(name, "bone", cells, cancer_risk)
        self.mineral_density = (
            mineral_density  # Higher density indicates stronger bones
        )
        self.osteoclast_activity = (
            0.01  # Represents bone resorption activity (osteoclasts)
        )
        self.osteoblast_activity = (
            0.02  # Represents bone formation activity (osteoblasts)
        )

    def increase_mineral_density(self, amount: float) -> None:
        """
        Increase the mineral density of the bone tissue.

        :param amount: The amount by which to increase mineral density
        """
        self.mineral_density += amount
        self.mineral_density = min(
            2.0, self.mineral_density
        )  # Cap the density at 2.0 for safety

    def decrease_mineral_density(self, amount: float) -> None:
        """
        Decrease the mineral density of the bone tissue.

        :param amount: The amount by which to decrease mineral density
        """
        self.mineral_density -= amount
        self.mineral_density = max(
            0.1, self.mineral_density
        )  # Ensure density doesn't drop too low

    def simulate_bone_remodeling(self) -> None:
        """
        Simulate bone remodeling, balancing osteoclast and osteoblast activities.
        Osteoclasts break down bone tissue, while osteoblasts help build new bone.
        """
        bone_resorption = self.get_cell_count() * self.osteoclast_activity
        bone_formation = self.get_cell_count() * self.osteoblast_activity
        self.remove_cells(int(bone_resorption))
        self.simulate_growth(amount=bone_formation)

    def simulate_growth(self, amount: float = None) -> None:
        """
        Override the tissue growth to consider bone-specific growth behavior.
        """
        if amount is None:
            amount = int(
                self.get_cell_count() * self.growth_rate * self.mineral_density
            )
        for _ in range(amount):
            new_cell = Cell(
                f"BoneCell_{random.randint(1000, 9999)}", str(random.uniform(85, 100))
            )
            self.add_cell(new_cell)

    def simulate_wound_healing(self, wound_size: int) -> None:
        """
        Simulate bone-specific wound healing, potentially adjusting mineral density.
        """
        super().simulate_wound_healing(wound_size)
        self.increase_mineral_density(
            wound_size * 0.01
        )  # Increase density slightly as new bone forms

    def apply_stress(self, stress_amount: float) -> None:
        """
        Apply stress to bone tissue, considering bone-specific reactions like micro-fractures.
        """
        super().apply_stress(stress_amount)
        self.decrease_mineral_density(
            stress_amount * 0.02
        )  # Higher stress reduces bone density slightly

    def describe(self) -> str:
        """Provide a detailed description of the bone tissue."""
        base_description = super().describe()
        additional_info = [
            f"Mineral Density: {self.mineral_density:.2f}",
            f"Osteoclast Activity: {self.osteoclast_activity:.2%}",
            f"Osteoblast Activity: {self.osteoblast_activity:.2%}",
        ]
        return base_description + "\n" + "\n".join(additional_info)

    def to_json(self) -> str:
        """Return a JSON representation of the bone tissue, including bone-specific attributes."""
        import json

        base_data = json.loads(super().to_json())
        base_data.update(
            {
                "mineral_density": self.mineral_density,
                "osteoclast_activity": self.osteoclast_activity,
                "osteoblast_activity": self.osteoblast_activity,
            }
        )
        return json.dumps(base_data)

    @classmethod
    def from_json(cls, json_str: str) -> "BoneTissue":
        """Load a bone tissue from a JSON string."""
        import json

        tissue_dict = json.loads(json_str)
        cells = [Cell.from_json(cell_json) for cell_json in tissue_dict["cells"]]
        bone_tissue = cls(
            name=tissue_dict["name"],
            cells=cells,
            cancer_risk=tissue_dict.get("cancer_risk", 0.001),
            mineral_density=tissue_dict.get("mineral_density", 1.0),
        )
        bone_tissue.osteoclast_activity = tissue_dict["osteoclast_activity"]
        bone_tissue.osteoblast_activity = tissue_dict["osteoblast_activity"]
        bone_tissue.growth_rate = tissue_dict["growth_rate"]
        bone_tissue.healing_rate = tissue_dict["healing_rate"]
        return bone_tissue
