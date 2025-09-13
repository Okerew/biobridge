import random
from typing import Any, Dict, List, Optional

from biobridge.blocks.tissue import Tissue
from biobridge.definitions.cells.organ import OrganCell


class OrganTissue(Tissue):
    def __init__(
        self,
        name: str,
        cells: Optional[List[OrganCell]] = None,
        cancer_risk: float = 0.005,
        organ_type: str = "generic",
        organ_function: float = 1.0,
        metabolic_rate: float = 0.5,
    ):
        """
        Initialize a new OrganTissue object, inheriting from Tissue.

        :param name: Name of the organ tissue
        :param cells: List of OrganCell objects that make up the organ tissue
        :param cancer_risk: The risk of cancer for this tissue type
        :param organ_type: Type of organ (liver, kidney, heart, lung, brain, etc.)
        :param organ_function: Current functional capacity (0.0 to 1.0)
        :param metabolic_rate: Metabolic activity rate (0.0 to 2.0)
        """
        super().__init__(
            name, tissue_type="organ", cells=cells, cancer_risk=cancer_risk
        )

        self.organ_type = organ_type
        self.organ_function = max(0.0, min(1.0, organ_function))
        self.metabolic_rate = max(0.0, min(2.0, metabolic_rate))

        # Organ-specific properties
        self.perfusion_rate = 0.7  # Blood flow rate (0.0 to 1.0)
        self.oxygen_consumption = 0.4  # Oxygen consumption rate
        self.toxin_clearance_rate = 0.3  # Rate at which toxins are cleared
        self.regeneration_capacity = 0.2  # Ability to regenerate damaged cells
        self.inflammation_level = 0.0  # Current inflammation level
        self.fibrosis_level = 0.0  # Level of fibrotic tissue

        # Organ-type specific initialization
        self._initialize_organ_specifics()

    def _initialize_organ_specifics(self):
        """Initialize organ-specific properties based on organ type."""
        organ_configs = {
            "liver": {
                "regeneration_capacity": 0.8,
                "toxin_clearance_rate": 0.9,
                "metabolic_rate": 1.5,
                "perfusion_rate": 0.9,
            },
            "kidney": {
                "toxin_clearance_rate": 0.95,
                "perfusion_rate": 0.85,
                "regeneration_capacity": 0.3,
                "oxygen_consumption": 0.6,
            },
            "heart": {
                "perfusion_rate": 0.95,
                "oxygen_consumption": 0.8,
                "metabolic_rate": 1.2,
                "regeneration_capacity": 0.1,
            },
            "lung": {
                "perfusion_rate": 0.8,
                "oxygen_consumption": 0.3,
                "toxin_clearance_rate": 0.4,
                "regeneration_capacity": 0.4,
            },
            "brain": {
                "oxygen_consumption": 0.9,
                "perfusion_rate": 0.8,
                "metabolic_rate": 1.3,
                "regeneration_capacity": 0.05,
            },
            "pancreas": {
                "metabolic_rate": 1.1,
                "regeneration_capacity": 0.2,
                "perfusion_rate": 0.7,
                "toxin_clearance_rate": 0.3,
            },
            "spleen": {
                "perfusion_rate": 0.6,
                "toxin_clearance_rate": 0.7,
                "regeneration_capacity": 0.4,
                "oxygen_consumption": 0.4,
            },
        }

        if self.organ_type in organ_configs:
            config = organ_configs[self.organ_type]
            for property_name, value in config.items():
                setattr(self, property_name, value)

    def perform_organ_function(self):
        """Simulate the primary function of the organ tissue."""
        if self.organ_function <= 0.1:
            print(
                f"{self.name} function severely impaired. Cannot perform normal operations."
            )
            return

        # Calculate functional efficiency based on current state
        efficiency = (
            self.organ_function
            * (1.0 - self.inflammation_level * 0.5)
            * (1.0 - self.fibrosis_level * 0.3)
        )
        efficiency = max(0.1, efficiency)

        print(
            f"Performing {self.organ_type} function for {self.name} at {efficiency:.1%} efficiency..."
        )

        # Organ-specific functions
        if self.organ_type == "liver":
            self._perform_liver_function(efficiency)
        elif self.organ_type == "kidney":
            self._perform_kidney_function(efficiency)
        elif self.organ_type == "heart":
            self._perform_heart_function(efficiency)
        elif self.organ_type == "lung":
            self._perform_lung_function(efficiency)
        elif self.organ_type == "brain":
            self._perform_brain_function(efficiency)
        else:
            self._perform_generic_function(efficiency)

        # Consume oxygen and nutrients
        self._consume_resources(efficiency)

    def _perform_liver_function(self, efficiency: float):
        """Simulate liver-specific functions."""
        # Detoxification
        toxins_cleared = self.toxin_clearance_rate * efficiency
        print(f"  - Cleared {toxins_cleared:.2f} units of toxins")

        # Protein synthesis
        protein_synthesis = self.metabolic_rate * efficiency * 0.7
        print(f"  - Synthesized {protein_synthesis:.2f} units of proteins")

        # Bile production
        bile_production = efficiency * 0.8
        print(f"  - Produced {bile_production:.2f} units of bile")

    def _perform_kidney_function(self, efficiency: float):
        """Simulate kidney-specific functions."""
        # Filtration
        filtration_rate = self.perfusion_rate * efficiency * 120  # ml/min approx
        print(f"  - Filtration rate: {filtration_rate:.1f} ml/min")

        # Toxin clearance
        toxins_cleared = self.toxin_clearance_rate * efficiency
        print(f"  - Cleared {toxins_cleared:.2f} units of waste products")

        # Electrolyte balance
        electrolyte_balance = efficiency * 0.9
        print(f"  - Maintained electrolyte balance at {electrolyte_balance:.1%}")

    def _perform_heart_function(self, efficiency: float):
        """Simulate heart-specific functions."""
        # Cardiac output
        cardiac_output = self.perfusion_rate * efficiency * 5.0  # L/min approx
        print(f"  - Cardiac output: {cardiac_output:.1f} L/min")

        # Pressure generation
        pressure_generation = efficiency * 120  # mmHg approx
        print(f"  - Systolic pressure generation: {pressure_generation:.0f} mmHg")

    def _perform_lung_function(self, efficiency: float):
        """Simulate lung-specific functions."""
        # Gas exchange
        oxygen_uptake = efficiency * self.perfusion_rate * 250  # ml/min approx
        print(f"  - Oxygen uptake: {oxygen_uptake:.1f} ml/min")

        # CO2 elimination
        co2_elimination = efficiency * 200  # ml/min approx
        print(f"  - CO2 elimination: {co2_elimination:.1f} ml/min")

    def _perform_brain_function(self, efficiency: float):
        """Simulate brain-specific functions."""
        # Neural activity
        neural_activity = efficiency * self.oxygen_consumption
        print(f"  - Neural activity level: {neural_activity:.1%}")

        # Neurotransmitter production
        neurotransmitter_production = efficiency * self.metabolic_rate * 0.6
        print(
            f"  - Neurotransmitter production: {neurotransmitter_production:.2f} units"
        )

    def _perform_generic_function(self, efficiency: float):
        """Simulate generic organ functions."""
        functional_output = efficiency * self.metabolic_rate
        print(f"  - Functional output: {functional_output:.2f} units")

    def _consume_resources(self, efficiency: float):
        """Consume oxygen and nutrients based on metabolic activity."""
        oxygen_consumed = self.oxygen_consumption * efficiency
        nutrients_consumed = self.metabolic_rate * efficiency * 0.8

        # This could interact with a circulatory system in a larger simulation
        print(f"  - Consumed {oxygen_consumed:.2f} units of oxygen")
        print(f"  - Consumed {nutrients_consumed:.2f} units of nutrients")

    def regenerate_tissue(self):
        """Simulate tissue regeneration and repair."""
        if self.regeneration_capacity <= 0.05:
            print(f"{self.name} has minimal regenerative capacity.")
            return

        # Calculate regeneration based on capacity and current damage
        damage_level = 1.0 - self.organ_function
        regeneration_amount = self.regeneration_capacity * damage_level * 0.1

        if regeneration_amount > 0.01:
            self.organ_function = min(1.0, self.organ_function + regeneration_amount)

            # Regenerate damaged cells
            damaged_cells = [
                cell
                for cell in self.cells
                if isinstance(cell, OrganCell) and cell.health < 80
            ]
            regenerated_count = 0

            for cell in damaged_cells[: int(len(damaged_cells) * regeneration_amount)]:
                cell.heal(regeneration_amount * 20)  # Heal by up to 20% * regen_amount
                regenerated_count += 1

            print(f"Regenerated {regenerated_count} cells in {self.name}")
            print(f"Organ function improved to {self.organ_function:.1%}")

    def process_toxins(self, toxin_load: float):
        """Process and clear toxins from the tissue."""
        if self.toxin_clearance_rate <= 0.1:
            print(f"{self.name} has poor toxin clearance capability.")
            self.damage_from_toxins(toxin_load * 0.8)
            return

        cleared_amount = min(
            toxin_load, self.toxin_clearance_rate * self.organ_function
        )
        remaining_toxins = toxin_load - cleared_amount

        print(f"Cleared {cleared_amount:.2f} units of toxins")

        if remaining_toxins > 0:
            self.damage_from_toxins(remaining_toxins * 0.3)

    def damage_from_toxins(self, toxin_amount: float):
        """Apply damage from unprocessed toxins."""
        damage_to_function = toxin_amount * 0.05
        damage_to_cells = toxin_amount * 0.1

        self.organ_function = max(0.0, self.organ_function - damage_to_function)
        self.inflammation_level = min(
            1.0, self.inflammation_level + toxin_amount * 0.02
        )

        # Damage random cells
        num_cells_to_damage = min(len(self.cells), int(damage_to_cells * 10))
        damaged_cells = random.sample(self.cells, num_cells_to_damage)

        for cell in damaged_cells:
            if isinstance(cell, OrganCell):
                cell.damage(damage_to_cells * 5)

        print(
            f"Toxin damage: Function reduced by {damage_to_function:.3f}, {num_cells_to_damage} cells damaged"
        )

    def apply_inflammation(self, inflammation_source: str, severity: float = 0.1):
        """Apply inflammatory response to the tissue."""
        self.inflammation_level = min(1.0, self.inflammation_level + severity)

        # Inflammation reduces organ function temporarily
        function_reduction = severity * 0.5
        self.organ_function = max(0.1, self.organ_function - function_reduction)

        # Increase metabolic rate due to inflammatory response
        self.metabolic_rate = min(2.0, self.metabolic_rate + severity * 0.3)

        print(f"Inflammation in {self.name} from {inflammation_source}")
        print(
            f"Inflammation level: {self.inflammation_level:.2f}, Function: {self.organ_function:.1%}"
        )

        # Some cells may die from severe inflammation
        if severity > 0.3:
            cells_affected = int(len(self.cells) * severity * 0.1)
            for _ in range(cells_affected):
                if self.cells:
                    cell = random.choice(self.cells)
                    if isinstance(cell, OrganCell):
                        cell.damage(severity * 30)

    def resolve_inflammation(self, resolution_rate: float = 0.05):
        """Resolve inflammatory processes."""
        if self.inflammation_level > 0:
            self.inflammation_level = max(
                0.0, self.inflammation_level - resolution_rate
            )

            # As inflammation resolves, some function may return
            function_recovery = resolution_rate * 0.3
            self.organ_function = min(1.0, self.organ_function + function_recovery)

            print(
                f"Inflammation resolving in {self.name}: {self.inflammation_level:.2f}"
            )

    def develop_fibrosis(self, fibrosis_trigger: str, severity: float = 0.05):
        """Develop fibrotic tissue in response to chronic damage."""
        self.fibrosis_level = min(1.0, self.fibrosis_level + severity)

        # Fibrosis permanently reduces organ function and regeneration capacity
        function_loss = severity * 0.7
        self.organ_function = max(0.1, self.organ_function - function_loss)
        self.regeneration_capacity = max(
            0.0, self.regeneration_capacity - severity * 0.2
        )

        print(f"Fibrosis developing in {self.name} due to {fibrosis_trigger}")
        print(
            f"Fibrosis level: {self.fibrosis_level:.2f}, Permanent function loss: {function_loss:.3f}"
        )

    def simulate_time_step(self, external_factors: List[tuple] = None):
        """Override the simulate_time_step method to include organ-specific behavior."""
        super().simulate_time_step(external_factors)

        # Perform organ function
        if random.random() < 0.8:  # 80% chance of performing function
            self.perform_organ_function()

        # Natural regeneration
        if random.random() < 0.3:  # 30% chance of regeneration attempt
            self.regenerate_tissue()

        # Resolve inflammation naturally
        if self.inflammation_level > 0 and random.random() < 0.4:
            self.resolve_inflammation()

        # Process external factors
        if external_factors:
            for factor_type, factor_value in external_factors:
                if factor_type == "toxin_exposure":
                    self.process_toxins(factor_value)
                elif factor_type == "inflammation":
                    self.apply_inflammation("external", factor_value)
                elif factor_type == "hypoxia":
                    self.apply_hypoxia(factor_value)
                elif factor_type == "nutrient_deficiency":
                    self.apply_nutrient_deficiency(factor_value)

    def apply_hypoxia(self, hypoxia_level: float):
        """Apply effects of oxygen deficiency."""
        function_reduction = hypoxia_level * 0.4
        self.organ_function = max(0.1, self.organ_function - function_reduction)

        # Cells may die from severe hypoxia
        if hypoxia_level > 0.5:
            cells_affected = int(len(self.cells) * hypoxia_level * 0.1)
            for _ in range(cells_affected):
                if self.cells:
                    cell = random.choice(self.cells)
                    if isinstance(cell, OrganCell):
                        cell.damage(hypoxia_level * 25)

        print(f"Hypoxia in {self.name}: Function reduced by {function_reduction:.3f}")

    def apply_nutrient_deficiency(self, deficiency_level: float):
        """Apply effects of nutrient deficiency."""
        metabolic_reduction = deficiency_level * 0.3
        self.metabolic_rate = max(0.1, self.metabolic_rate - metabolic_reduction)

        regeneration_reduction = deficiency_level * 0.2
        self.regeneration_capacity = max(
            0.0, self.regeneration_capacity - regeneration_reduction
        )

        print(
            f"Nutrient deficiency in {self.name}: Metabolic rate reduced by {metabolic_reduction:.3f}"
        )

    def get_functional_status(self) -> Dict[str, Any]:
        """Get comprehensive functional status of the organ tissue."""
        return {
            "organ_function": self.organ_function,
            "metabolic_rate": self.metabolic_rate,
            "perfusion_rate": self.perfusion_rate,
            "inflammation_level": self.inflammation_level,
            "fibrosis_level": self.fibrosis_level,
            "regeneration_capacity": self.regeneration_capacity,
            "toxin_clearance_rate": self.toxin_clearance_rate,
            "oxygen_consumption": self.oxygen_consumption,
            "functional_efficiency": self.organ_function
            * (1.0 - self.inflammation_level * 0.5)
            * (1.0 - self.fibrosis_level * 0.3),
        }

    def describe(self) -> str:
        """Provide a detailed description of the organ tissue."""
        base_description = super().describe()
        status = self.get_functional_status()

        additional_info = [
            f"Organ Type: {self.organ_type.capitalize()}",
            f"Functional Capacity: {status['organ_function']:.1%}",
            f"Metabolic Rate: {status['metabolic_rate']:.2f}",
            f"Inflammation Level: {status['inflammation_level']:.2f}",
            f"Fibrosis Level: {status['fibrosis_level']:.2f}",
            f"Regeneration Capacity: {status['regeneration_capacity']:.2f}",
            f"Overall Efficiency: {status['functional_efficiency']:.1%}",
        ]

        return f"{base_description}\n" + "\n".join(additional_info)
