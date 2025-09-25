import random
from typing import List, Optional

from biobridge.blocks.cell import Cell
from biobridge.blocks.tissue import Tissue


class BreastTissue(Tissue):
    def __init__(
        self,
        name: str,
        cells: Optional[List[Cell]] = None,
        cancer_risk: float = 0.001,
        mammographic_density: float = 0.5,
        birads_category: str = "B",
    ):
        """
        Initialize a new BreastTissue object.

        :param name: Name of the breast tissue
        :param cells: List of Cell objects that make up the breast tissue
        :param cancer_risk: Risk of cancer in breast tissue
        :param mammographic_density: Mammographic density (0-1 scale)
        :param birads_category: BI-RADS density category (A, B, C, D)
        """
        super().__init__(name, "breast", cells, cancer_risk)
        self.mammographic_density = mammographic_density
        self.birads_category = birads_category
        self.ductal_activity = 0.03
        self.stromal_activity = 0.02
        self.fat_content = 1.0 - mammographic_density
        self.fibroglandular_content = mammographic_density

    def increase_density(self, amount: float) -> None:
        """
        Increase the mammographic density of the breast tissue.

        :param amount: The amount by which to increase density
        """
        self.mammographic_density += amount
        self.mammographic_density = min(1.0, self.mammographic_density)
        self.fat_content = 1.0 - self.mammographic_density
        self.fibroglandular_content = self.mammographic_density
        self._update_birads_category()

    def decrease_density(self, amount: float) -> None:
        """
        Decrease the mammographic density of the breast tissue.

        :param amount: The amount by which to decrease density
        """
        self.mammographic_density -= amount
        self.mammographic_density = max(0.0, self.mammographic_density)
        self.fat_content = 1.0 - self.mammographic_density
        self.fibroglandular_content = self.mammographic_density
        self._update_birads_category()

    def _update_birads_category(self) -> None:
        """Update BI-RADS category based on current density."""
        density_percentage = self.mammographic_density * 100
        if density_percentage < 10:
            self.birads_category = "A"
        elif density_percentage < 25:
            self.birads_category = "B"
        elif density_percentage < 50:
            self.birads_category = "C"
        else:
            self.birads_category = "D"

    def simulate_hormonal_changes(self, hormone_level: float) -> None:
        """
        Simulate hormonal effects on breast tissue.

        :param hormone_level: Hormone level (0-1 scale)
        """
        density_change = hormone_level * 0.1
        self.increase_density(density_change)
        
        activity_change = hormone_level * 0.01
        self.ductal_activity += activity_change
        self.stromal_activity += activity_change
        
        self.ductal_activity = min(0.1, max(0.01, self.ductal_activity))
        self.stromal_activity = min(0.1, max(0.01, self.stromal_activity))

    def simulate_breast_remodeling(self) -> None:
        """
        Simulate breast tissue remodeling with ductal and stromal changes.
        """
        ductal_changes = self.get_cell_count() * self.ductal_activity
        stromal_changes = self.get_cell_count() * self.stromal_activity
        
        total_changes = int((ductal_changes + stromal_changes) / 2)
        self.remove_cells(total_changes // 2)
        self.simulate_growth(amount=total_changes)

    def simulate_growth(self, amount: float = None) -> None:
        """
        Override tissue growth for breast-specific behavior.
        """
        if amount is None:
            density_factor = 1.0 + (self.mammographic_density * 0.5)
            amount = int(self.get_cell_count() * self.growth_rate * density_factor)
        
        for _ in range(int(amount)):
            cell_type = "ductal" if random.random() < 0.6 else "stromal"
            new_cell = Cell(
                f"BreastCell_{cell_type}_{random.randint(1000, 9999)}",
                str(random.uniform(80, 98))
            )
            self.add_cell(new_cell)

    def apply_compression(self, compression_force: float) -> None:
        """
        Apply mammographic compression effects.

        :param compression_force: Force of compression (0-1 scale)
        """
        stress_amount = compression_force * 0.5
        super().apply_stress(stress_amount)
        
        temporary_density_increase = compression_force * 0.1
        self.mammographic_density = min(
            1.0, self.mammographic_density + temporary_density_increase
        )

    def detect_architectural_changes(self) -> dict:
        """
        Detect changes in breast architecture that might indicate pathology.

        :return: Dictionary of architectural change indicators
        """
        changes = {}
        
        if self.cancer_risk > 0.05:
            changes["high_risk_pattern"] = True
        
        if self.ductal_activity > 0.07:
            changes["increased_ductal_activity"] = True
        
        if self.mammographic_density > 0.75:
            changes["extremely_dense"] = True
        
        cell_health_avg = sum(float(cell.health) for cell in self.cells) / len(
            self.cells
        ) if self.cells else 100
        if cell_health_avg < 85:
            changes["cellular_dysfunction"] = True
        
        return changes

    def simulate_aging(self, years: float) -> None:
        """
        Simulate aging effects on breast tissue.

        :param years: Number of years to simulate
        """
        density_decrease = years * 0.01
        self.decrease_density(density_decrease)
        
        activity_decrease = years * 0.001
        self.ductal_activity = max(0.01, self.ductal_activity - activity_decrease)
        self.stromal_activity = max(0.01, self.stromal_activity - activity_decrease)
        
        for cell in self.cells:
            health_decrease = years * random.uniform(0.5, 1.5)
            new_health = max(60.0, float(cell.health) - health_decrease)
            cell.health = str(new_health)

    def get_density_category_description(self) -> str:
        """Get description of current BI-RADS density category."""
        descriptions = {
            "A": "Almost entirely fatty",
            "B": "Scattered areas of fibroglandular density",
            "C": "Heterogeneously dense",
            "D": "Extremely dense",
        }
        return descriptions.get(self.birads_category, "Unknown")

    def describe(self) -> str:
        """Provide detailed description of the breast tissue."""
        base_description = super().describe()
        additional_info = [
            f"Mammographic Density: {self.mammographic_density:.2f}",
            f"BI-RADS Category: {self.birads_category}",
            f"Density Description: {self.get_density_category_description()}",
            f"Fat Content: {self.fat_content:.2%}",
            f"Fibroglandular Content: {self.fibroglandular_content:.2%}",
            f"Ductal Activity: {self.ductal_activity:.2%}",
            f"Stromal Activity: {self.stromal_activity:.2%}",
        ]
        return base_description + "\n" + "\n".join(additional_info)

    def to_json(self) -> str:
        """Return JSON representation including breast-specific attributes."""
        import json

        base_data = json.loads(super().to_json())
        base_data.update({
            "mammographic_density": self.mammographic_density,
            "birads_category": self.birads_category,
            "ductal_activity": self.ductal_activity,
            "stromal_activity": self.stromal_activity,
            "fat_content": self.fat_content,
            "fibroglandular_content": self.fibroglandular_content,
        })
        return json.dumps(base_data)

    @classmethod
    def from_json(cls, json_str: str) -> "BreastTissue":
        """Load breast tissue from JSON string."""
        import json

        tissue_dict = json.loads(json_str)
        cells = [Cell.from_json(cell_json) for cell_json in tissue_dict["cells"]]
        breast_tissue = cls(
            name=tissue_dict["name"],
            cells=cells,
            cancer_risk=tissue_dict.get("cancer_risk", 0.001),
            mammographic_density=tissue_dict.get("mammographic_density", 0.5),
            birads_category=tissue_dict.get("birads_category", "B"),
        )
        breast_tissue.ductal_activity = tissue_dict.get("ductal_activity", 0.03)
        breast_tissue.stromal_activity = tissue_dict.get("stromal_activity", 0.02)
        breast_tissue.fat_content = tissue_dict.get("fat_content", 0.5)
        breast_tissue.fibroglandular_content = tissue_dict.get(
            "fibroglandular_content", 0.5
        )
        breast_tissue.growth_rate = tissue_dict.get("growth_rate", 0.05)
        breast_tissue.healing_rate = tissue_dict.get("healing_rate", 0.1)
        return breast_tissue
