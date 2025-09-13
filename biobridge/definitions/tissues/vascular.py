import random
from typing import List, Optional

from biobridge.blocks.cell import Cell
from biobridge.blocks.tissue import Tissue


class VascularTissue(Tissue):
    def __init__(
        self,
        name: str,
        cells: Optional[List[Cell]] = None,
        cardiovascular_risk: float = 0.001,
        blood_flow: float = 1.0,
        oxygen_delivery: float = 0.8,
    ):
        """
        Initialize a new VascularTissue object.

        :param name: Name of the vascular tissue
        :param cells: List of Cell objects that make up the vascular tissue (endothelial cells, smooth muscle cells, etc.)
        :param cardiovascular_risk: Risk of cardiovascular events in this tissue
        :param blood_flow: Relative blood flow through this tissue (1.0 = normal)
        :param oxygen_delivery: Oxygen delivery efficiency (0.0-1.0 scale)
        """
        super().__init__(name, "vascular", cells, cardiovascular_risk)
        self.blood_flow = blood_flow  # Blood flow rate through vessels
        self.oxygen_delivery = oxygen_delivery  # Oxygen delivery efficiency
        self.vessel_diameter = 1.0  # Average vessel diameter (relative scale)
        self.endothelial_function = 0.9  # Endothelial function score (0.0-1.0)
        self.vasodilation_capacity = 0.8  # Ability to dilate vessels (0.0-1.0)
        self.vasoconstriction_capacity = 0.8  # Ability to constrict vessels (0.0-1.0)
        self.nitric_oxide_production = 0.75  # NO production for vasodilation
        self.platelet_aggregation = (
            0.1  # Tendency for platelet clumping (lower is better)
        )

        # Pathology tracking
        self.stenosis_severity = 0.0  # Degree of vessel narrowing (0.0-1.0)
        self.aneurysm_risk = 0.0  # Risk of vessel dilation/rupture (0.0-1.0)
        self.atherosclerotic_burden = 0.0  # Amount of plaque buildup (0.0-1.0)

    def increase_blood_flow(self, amount: float) -> None:
        """
        Increase blood flow through the vascular tissue.

        :param amount: The amount by which to increase blood flow
        """
        self.blood_flow += amount
        self.blood_flow = min(3.0, self.blood_flow)  # Cap at 3x normal flow
        # Improved flow often improves oxygen delivery
        self.oxygen_delivery = min(1.0, self.oxygen_delivery + amount * 0.1)

    def decrease_blood_flow(self, amount: float) -> None:
        """
        Decrease blood flow through the vascular tissue.

        :param amount: The amount by which to decrease blood flow
        """
        self.blood_flow -= amount
        self.blood_flow = max(0.1, self.blood_flow)  # Maintain minimal flow
        # Reduced flow decreases oxygen delivery
        self.oxygen_delivery = max(0.1, self.oxygen_delivery - amount * 0.15)

    def simulate_vasodilation(self, stimulus_strength: float = 0.2) -> None:
        """
        Simulate vessel dilation in response to various stimuli.

        :param stimulus_strength: Strength of vasodilation stimulus
        """
        if self.vasodilation_capacity > 0:
            dilation_response = (
                stimulus_strength
                * self.vasodilation_capacity
                * self.nitric_oxide_production
            )
            self.vessel_diameter += dilation_response
            self.vessel_diameter = min(
                2.0, self.vessel_diameter
            )  # Cap maximum dilation

            # Dilation improves blood flow
            flow_increase = dilation_response * 0.5
            self.increase_blood_flow(flow_increase)

    def simulate_vasoconstriction(self, stimulus_strength: float = 0.2) -> None:
        """
        Simulate vessel constriction in response to various stimuli.

        :param stimulus_strength: Strength of vasoconstriction stimulus
        """
        if self.vasoconstriction_capacity > 0:
            constriction_response = stimulus_strength * self.vasoconstriction_capacity
            self.vessel_diameter -= constriction_response
            self.vessel_diameter = max(
                0.3, self.vessel_diameter
            )  # Maintain minimal diameter

            # Constriction reduces blood flow
            flow_decrease = constriction_response * 0.6
            self.decrease_blood_flow(flow_decrease)

    def develop_atherosclerosis(self, plaque_amount: float) -> None:
        """
        Simulate development of atherosclerotic plaque.

        :param plaque_amount: Amount of plaque to add (0.0-1.0)
        """
        self.atherosclerotic_burden += plaque_amount
        self.atherosclerotic_burden = min(1.0, self.atherosclerotic_burden)

        # Plaque buildup affects vessel function
        self.stenosis_severity += plaque_amount * 0.8
        self.stenosis_severity = min(1.0, self.stenosis_severity)

        # Reduce vessel function
        self.endothelial_function *= 1.0 - plaque_amount * 0.3
        self.nitric_oxide_production *= 1.0 - plaque_amount * 0.25

        # Decrease flow due to narrowing
        self.decrease_blood_flow(plaque_amount * 0.5)

    def simulate_angiogenesis(self, growth_factor: float = 0.1) -> None:
        """
        Simulate formation of new blood vessels (angiogenesis).

        :param growth_factor: Strength of angiogenic stimulus
        """
        # Create new endothelial cells
        new_vessel_cells = int(self.get_cell_count() * growth_factor)
        for i in range(new_vessel_cells):
            new_cell = Cell(
                f"EndothelialCell_{random.randint(1000, 9999)}",
                str(random.uniform(80, 95)),
            )
            self.add_cell(new_cell)

        # Improve vascular capacity
        self.increase_blood_flow(growth_factor * 0.3)
        self.oxygen_delivery = min(1.0, self.oxygen_delivery + growth_factor * 0.2)

    def simulate_thrombosis_risk(self) -> float:
        """
        Calculate the risk of thrombosis (blood clot formation).

        :return: Thrombosis risk score (0.0-1.0)
        """
        risk_factors = [
            self.platelet_aggregation,
            (
                1.0 - self.blood_flow if self.blood_flow < 1.0 else 0.0
            ),  # Stasis increases risk
            self.atherosclerotic_burden * 0.5,
            1.0 - self.endothelial_function,
        ]

        base_risk = sum(risk_factors) / len(risk_factors)
        return min(1.0, base_risk)

    def simulate_growth(self, amount: float = None) -> None:
        """
        Override tissue growth to consider vascular-specific growth behavior.
        """
        for _ in range(int(amount)):
            # Create mix of endothelial and smooth muscle cells
            cell_type = (
                "EndothelialCell" if random.random() < 0.7 else "SmoothMuscleCell"
            )
            new_cell = Cell(
                f"{cell_type}_{random.randint(1000, 9999)}", str(random.uniform(75, 95))
            )
            self.add_cell(new_cell)

    def simulate_wound_healing(self, wound_size: int) -> None:
        """
        Simulate vascular-specific wound healing with angiogenesis.
        """
        super().simulate_wound_healing(wound_size)
        # Wound healing stimulates vessel growth
        angiogenic_response = wound_size * 0.02
        self.simulate_angiogenesis(angiogenic_response)

    def apply_stress(self, stress_amount: float) -> None:
        """
        Apply stress to vascular tissue, considering vessel-specific reactions.
        """
        super().apply_stress(stress_amount)

        # Stress affects vascular function
        self.endothelial_function *= 1.0 - stress_amount * 0.05
        self.endothelial_function = max(0.1, self.endothelial_function)

        # May trigger vasoconstriction
        self.simulate_vasoconstriction(stress_amount * 0.3)

        # Increase platelet aggregation
        self.platelet_aggregation += stress_amount * 0.02
        self.platelet_aggregation = min(1.0, self.platelet_aggregation)

    def calculate_vascular_health_score(self) -> float:
        """
        Calculate overall vascular health score.

        :return: Health score (0.0-1.0, higher is better)
        """
        positive_factors = [
            self.blood_flow / 3.0,  # Normalize to 0-1
            self.oxygen_delivery,
            self.endothelial_function,
            self.vasodilation_capacity,
            self.nitric_oxide_production,
        ]

        negative_factors = [
            self.stenosis_severity,
            self.aneurysm_risk,
            self.atherosclerotic_burden,
            self.platelet_aggregation,
            self.simulate_thrombosis_risk(),
        ]

        positive_score = sum(positive_factors) / len(positive_factors)
        negative_score = sum(negative_factors) / len(negative_factors)

        return max(0.0, positive_score - negative_score)

    def describe(self) -> str:
        """Provide a detailed description of the vascular tissue."""
        base_description = super().describe()
        health_score = self.calculate_vascular_health_score()
        thrombosis_risk = self.simulate_thrombosis_risk()

        additional_info = [
            f"Blood Flow: {self.blood_flow:.2f}x normal",
            f"Oxygen Delivery: {self.oxygen_delivery:.2%}",
            f"Vessel Diameter: {self.vessel_diameter:.2f}x normal",
            f"Endothelial Function: {self.endothelial_function:.2%}",
            f"Stenosis Severity: {self.stenosis_severity:.2%}",
            f"Atherosclerotic Burden: {self.atherosclerotic_burden:.2%}",
            f"Aneurysm Risk: {self.aneurysm_risk:.2%}",
            f"Thrombosis Risk: {thrombosis_risk:.2%}",
            f"Overall Vascular Health: {health_score:.2%}",
        ]
        return base_description + "\n" + "\n".join(additional_info)

    def to_json(self) -> str:
        """Return a JSON representation of the vascular tissue, including vascular-specific attributes."""
        import json

        base_data = json.loads(super().to_json())
        base_data.update(
            {
                "blood_flow": self.blood_flow,
                "oxygen_delivery": self.oxygen_delivery,
                "vessel_diameter": self.vessel_diameter,
                "endothelial_function": self.endothelial_function,
                "vasodilation_capacity": self.vasodilation_capacity,
                "vasoconstriction_capacity": self.vasoconstriction_capacity,
                "nitric_oxide_production": self.nitric_oxide_production,
                "platelet_aggregation": self.platelet_aggregation,
                "stenosis_severity": self.stenosis_severity,
                "aneurysm_risk": self.aneurysm_risk,
                "atherosclerotic_burden": self.atherosclerotic_burden,
            }
        )
        return json.dumps(base_data)

    @classmethod
    def from_json(cls, json_str: str) -> "VascularTissue":
        """Load a vascular tissue from a JSON string."""
        import json

        tissue_dict = json.loads(json_str)
        cells = [Cell.from_json(cell_json) for cell_json in tissue_dict["cells"]]

        vascular_tissue = cls(
            name=tissue_dict["name"],
            cells=cells,
            cardiovascular_risk=tissue_dict.get(
                "cancer_risk", 0.001
            ),  # Note: using cancer_risk key for backward compatibility
            blood_flow=tissue_dict.get("blood_flow", 1.0),
            oxygen_delivery=tissue_dict.get("oxygen_delivery", 0.8),
        )

        # Set additional attributes
        vascular_tissue.vessel_diameter = tissue_dict.get("vessel_diameter", 1.0)
        vascular_tissue.endothelial_function = tissue_dict.get(
            "endothelial_function", 0.9
        )
        vascular_tissue.vasodilation_capacity = tissue_dict.get(
            "vasodilation_capacity", 0.8
        )
        vascular_tissue.vasoconstriction_capacity = tissue_dict.get(
            "vasoconstriction_capacity", 0.8
        )
        vascular_tissue.nitric_oxide_production = tissue_dict.get(
            "nitric_oxide_production", 0.75
        )
        vascular_tissue.platelet_aggregation = tissue_dict.get(
            "platelet_aggregation", 0.1
        )
        vascular_tissue.stenosis_severity = tissue_dict.get("stenosis_severity", 0.0)
        vascular_tissue.aneurysm_risk = tissue_dict.get("aneurysm_risk", 0.0)
        vascular_tissue.atherosclerotic_burden = tissue_dict.get(
            "atherosclerotic_burden", 0.0
        )
        vascular_tissue.growth_rate = tissue_dict.get("growth_rate", 0.1)
        vascular_tissue.healing_rate = tissue_dict.get("healing_rate", 0.1)

        return vascular_tissue
