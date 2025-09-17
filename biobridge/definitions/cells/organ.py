import random
from typing import Any, Dict, Optional

from biobridge.blocks.cell import Cell


class OrganCell(Cell):
    def __init__(
        self,
        name: str,
        health: str,
        organ_type: str = "generic",
        cell_subtype: str = "parenchymal",
        metabolic_activity: float = 0.5,
        oxygen_consumption: float = 0.3,
        specialization_level: float = 0.7,
    ):
        """
        Initialize a new OrganCell object, inheriting from Cell.
        :param name: Name/identifier of the organ cell
        :param health: Health status as string (will be converted to float)
        :param organ_type: Type of organ this cell belongs to
        :param cell_subtype: Specific cell type within the organ
        :param metabolic_activity: Metabolic activity level (0.0 to 2.0)
        :param oxygen_consumption: Oxygen consumption rate (0.0 to 1.0)
        :param specialization_level: How specialized this cell is (0.0 to 1.0)
        """
        super().__init__(name, health)
        self.organ_type = organ_type
        self.cell_subtype = cell_subtype
        self.metabolic_activity = max(0.0, min(2.0, metabolic_activity))
        self.oxygen_consumption = max(0.0, min(1.0, oxygen_consumption))
        self.specialization_level = max(0.0, min(1.0, specialization_level))
        # Organ cell specific properties
        self.functional_capacity = 1.0  # Current functional capacity (0.0 to 1.0)
        self.protein_synthesis_rate = 0.4  # Rate of protein synthesis
        self.waste_production_rate = 0.3  # Rate of waste production
        self.regeneration_potential = 0.5  # Ability to divide/regenerate
        self.stress_resistance = 0.6  # Resistance to cellular stress
        self.toxin_sensitivity = 0.4  # Sensitivity to toxic substances
        # Cell state variables
        self.is_active = True
        self.is_dividing = False
        self.apoptotic = False
        self.senescent = False
        self.inflammation_markers = 0.0  # Level of inflammatory markers
        self.oxidative_stress = 0.0  # Level of oxidative stress
        self.autophagy_activity = 0.2  # Cellular cleanup activity
        # Organ-specific initialization
        self._initialize_organ_specifics()
        # Cell cycle and lifespan
        self.cell_age = 0  # Days since cell creation
        self.division_count = 0  # Number of times this cell has divided
        self.max_divisions = 50  # Hayflick limit
        self.lifespan_days = 365  # Default lifespan in days
        # Initialize based on cell subtype
        self._initialize_subtype_specifics()

    def damage(self, amount: float):
        """Damage the cell by decreasing its health by the specified amount."""
        self.health = max(0.0, self.health - amount)

    def heal(self, amount: float):
        """Heal the cell by increasing its health by the specified amount."""
        self.health = min(100.0, self.health + amount)

    def _initialize_organ_specifics(self):
        """Initialize organ-specific cellular properties."""
        organ_configs = {
            "liver": {
                "metabolic_activity": 1.8,
                "protein_synthesis_rate": 0.9,
                "regeneration_potential": 0.8,
                "toxin_sensitivity": 0.2,
                "lifespan_days": 150,
                "oxygen_consumption": 0.7,
            },
            "kidney": {
                "waste_production_rate": 0.1,
                "toxin_sensitivity": 0.3,
                "regeneration_potential": 0.3,
                "stress_resistance": 0.7,
                "lifespan_days": 730,
                "oxygen_consumption": 0.8,
            },
            "heart": {
                "metabolic_activity": 1.5,
                "regeneration_potential": 0.1,
                "stress_resistance": 0.8,
                "oxygen_consumption": 0.9,
                "lifespan_days": 7300,  # Heart cells live very long
                "specialization_level": 0.95,
            },
            "lung": {
                "oxygen_consumption": 0.4,
                "regeneration_potential": 0.6,
                "toxin_sensitivity": 0.6,
                "stress_resistance": 0.5,
                "lifespan_days": 21,  # Alveolar cells turnover quickly
                "waste_production_rate": 0.2,
            },
            "brain": {
                "metabolic_activity": 1.9,
                "oxygen_consumption": 0.95,
                "regeneration_potential": 0.05,
                "specialization_level": 0.98,
                "stress_resistance": 0.4,
                "lifespan_days": 25550,  # Brain cells live ~70 years
                "toxin_sensitivity": 0.8,
            },
            "pancreas": {
                "protein_synthesis_rate": 0.8,
                "metabolic_activity": 1.3,
                "regeneration_potential": 0.4,
                "specialization_level": 0.85,
                "lifespan_days": 365,
                "toxin_sensitivity": 0.5,
            },
            "spleen": {
                "regeneration_potential": 0.6,
                "stress_resistance": 0.6,
                "waste_production_rate": 0.5,
                "lifespan_days": 120,
                "metabolic_activity": 1.1,
            },
        }

        if self.organ_type in organ_configs:
            config = organ_configs[self.organ_type]
            for property_name, value in config.items():
                setattr(self, property_name, value)

    def _initialize_subtype_specifics(self):
        """Initialize cell subtype-specific properties."""
        # Define cell subtypes for different organs
        subtype_configs = {
            "hepatocyte": {  # Liver parenchymal cells
                "protein_synthesis_rate": 0.95,
                "metabolic_activity": 2.0,
                "toxin_sensitivity": 0.1,
            },
            "kupffer_cell": {  # Liver immune cells
                "waste_production_rate": 0.6,
                "stress_resistance": 0.8,
                "regeneration_potential": 0.7,
            },
            "nephron": {  # Kidney functional units
                "waste_production_rate": 0.05,
                "specialization_level": 0.9,
                "toxin_sensitivity": 0.2,
            },
            "cardiomyocyte": {  # Heart muscle cells
                "metabolic_activity": 1.8,
                "specialization_level": 0.98,
                "regeneration_potential": 0.05,
            },
            "pneumocyte_type1": {  # Lung gas exchange cells
                "oxygen_consumption": 0.3,
                "specialization_level": 0.85,
                "regeneration_potential": 0.4,
            },
            "pneumocyte_type2": {  # Lung surfactant-producing cells
                "protein_synthesis_rate": 0.8,
                "regeneration_potential": 0.7,
                "specialization_level": 0.8,
            },
            "neuron": {  # Brain nerve cells
                "metabolic_activity": 2.0,
                "oxygen_consumption": 0.98,
                "regeneration_potential": 0.02,
                "specialization_level": 0.99,
            },
            "astrocyte": {  # Brain support cells
                "stress_resistance": 0.7,
                "regeneration_potential": 0.3,
                "metabolic_activity": 1.2,
            },
            "beta_cell": {  # Pancreatic insulin-producing cells
                "protein_synthesis_rate": 0.9,
                "specialization_level": 0.95,
                "metabolic_activity": 1.4,
            },
            "acinar_cell": {  # Pancreatic enzyme-producing cells
                "protein_synthesis_rate": 0.95,
                "metabolic_activity": 1.6,
                "specialization_level": 0.8,
            },
        }

        if self.cell_subtype in subtype_configs:
            config = subtype_configs[self.cell_subtype]
            for property_name, value in config.items():
                setattr(self, property_name, value)

    def perform_cellular_function(self):
        """Perform the specialized function of this organ cell."""
        if not self.is_active or self.apoptotic:
            return

        # Calculate functional efficiency
        efficiency = (
            self.functional_capacity
            * (self.health / 100)
            * (1.0 - self.oxidative_stress * 0.3)
            * (1.0 - self.inflammation_markers * 0.2)
        )

        if self.organ_type == "liver":
            self._perform_liver_cell_function(efficiency)
        elif self.organ_type == "kidney":
            self._perform_kidney_cell_function(efficiency)
        elif self.organ_type == "heart":
            self._perform_heart_cell_function(efficiency)
        elif self.organ_type == "lung":
            self._perform_lung_cell_function(efficiency)
        elif self.organ_type == "brain":
            self._perform_brain_cell_function(efficiency)
        elif self.organ_type == "pancreas":
            self._perform_pancreas_cell_function(efficiency)
        else:
            self._perform_generic_function(efficiency)

        # Consume oxygen and produce waste
        self._metabolic_processes(efficiency)

    def _perform_liver_cell_function(self, efficiency: float):
        """Liver cell specific functions."""
        if self.cell_subtype == "hepatocyte":
            # Protein synthesis
            proteins_produced = self.protein_synthesis_rate * efficiency

            # Detoxification
            toxins_processed = efficiency * 0.8

            # Glucose metabolism
            glucose_processed = self.metabolic_activity * efficiency * 0.6

            self.functional_output = {
                "proteins_synthesized": proteins_produced,
                "toxins_detoxified": toxins_processed,
                "glucose_metabolized": glucose_processed,
            }

        elif self.cell_subtype == "kupffer_cell":
            # Immune function
            pathogens_cleared = efficiency * 0.7
            debris_cleared = self.waste_production_rate * efficiency

            self.functional_output = {
                "pathogens_phagocytosed": pathogens_cleared,
                "cellular_debris_cleared": debris_cleared,
            }

    def _perform_kidney_cell_function(self, efficiency: float):
        """Kidney cell specific functions."""
        if self.cell_subtype == "nephron":
            # Filtration
            filtration_rate = efficiency * 0.9

            # Reabsorption
            reabsorption_rate = efficiency * 0.8

            # Secretion
            secretion_rate = self.waste_production_rate * efficiency

            self.functional_output = {
                "filtration_performed": filtration_rate,
                "substances_reabsorbed": reabsorption_rate,
                "waste_secreted": secretion_rate,
            }

    def _perform_heart_cell_function(self, efficiency: float):
        """Heart cell specific functions."""
        if self.cell_subtype == "cardiomyocyte":
            # Contractile force generation
            contractile_force = efficiency * self.specialization_level

            # Electrical conduction
            conduction_velocity = efficiency * 0.9

            self.functional_output = {
                "contractile_force": contractile_force,
                "conduction_velocity": conduction_velocity,
                "energy_consumed": self.metabolic_activity * efficiency,
            }

    def _perform_lung_cell_function(self, efficiency: float):
        """Lung cell specific functions."""
        if self.cell_subtype == "pneumocyte_type1":
            # Gas exchange
            gas_exchange_rate = efficiency * 0.95

            self.functional_output = {
                "oxygen_transferred": gas_exchange_rate * 0.6,
                "co2_eliminated": gas_exchange_rate * 0.4,
            }

        elif self.cell_subtype == "pneumocyte_type2":
            # Surfactant production
            surfactant_produced = self.protein_synthesis_rate * efficiency

            self.functional_output = {
                "surfactant_produced": surfactant_produced,
                "alveolar_repair": efficiency * 0.3,
            }

    def _perform_brain_cell_function(self, efficiency: float):
        """Brain cell specific functions."""
        if self.cell_subtype == "neuron":
            # Neural signal transmission
            signal_transmission = efficiency * self.specialization_level

            # Neurotransmitter synthesis
            neurotransmitter_synthesis = self.protein_synthesis_rate * efficiency

            self.functional_output = {
                "signals_transmitted": signal_transmission,
                "neurotransmitters_synthesized": neurotransmitter_synthesis,
                "synaptic_activity": efficiency * 0.8,
            }

        elif self.cell_subtype == "astrocyte":
            # Support functions
            metabolic_support = efficiency * 0.7
            neurotransmitter_uptake = efficiency * 0.6

            self.functional_output = {
                "metabolic_support_provided": metabolic_support,
                "neurotransmitters_cleared": neurotransmitter_uptake,
                "blood_brain_barrier_maintenance": efficiency * 0.5,
            }

    def _perform_pancreas_cell_function(self, efficiency: float):
        """Pancreas cell specific functions."""
        if self.cell_subtype == "beta_cell":
            # Insulin production
            insulin_produced = self.protein_synthesis_rate * efficiency

            self.functional_output = {
                "insulin_secreted": insulin_produced,
                "glucose_sensing": efficiency * 0.9,
            }

        elif self.cell_subtype == "acinar_cell":
            # Digestive enzyme production
            enzymes_produced = self.protein_synthesis_rate * efficiency

            self.functional_output = {
                "digestive_enzymes_produced": enzymes_produced,
                "zymogen_granules_formed": efficiency * 0.8,
            }

    def _perform_generic_function(self, efficiency: float):
        """Generic organ cell function."""
        self.functional_output = {
            "general_metabolism": self.metabolic_activity * efficiency,
            "protein_synthesis": self.protein_synthesis_rate * efficiency,
            "cellular_maintenance": efficiency * 0.5,
        }

    def _metabolic_processes(self, efficiency: float):
        """Handle basic metabolic processes."""
        # Oxygen consumption
        if efficiency > 0.8:
            self.oxidative_stress = max(0.0, self.oxidative_stress - 0.01)
        else:
            self.oxidative_stress = min(1.0, self.oxidative_stress + 0.005)

    def divide(self) -> Optional["OrganCell"]:
        """Attempt cell division if conditions are met."""
        if (
            self.is_active
            and not self.senescent
            and not self.apoptotic
            and self.division_count < self.max_divisions
            and self.health > 70
            and random.random() < self.regeneration_potential
        ):

            # Create daughter cell
            daughter_name = f"{self.name}_div{self.division_count + 1}"
            daughter_health = str(max(60, self.health - random.uniform(0, 10)))

            daughter_cell = OrganCell(
                name=daughter_name,
                health=daughter_health,
                organ_type=self.organ_type,
                cell_subtype=self.cell_subtype,
                metabolic_activity=self.metabolic_activity * random.uniform(0.9, 1.1),
                oxygen_consumption=self.oxygen_consumption,
                specialization_level=self.specialization_level,
            )

            # Update division counts
            self.division_count += 1
            daughter_cell.division_count = self.division_count

            # Reduce health slightly after division
            self.health = max(50, self.health - random.uniform(2, 8))

            # Check for senescence
            if self.division_count >= self.max_divisions * 0.9:
                self.senescent = True
                self.regeneration_potential *= 0.1

            print(f"Cell {self.name} divided to create {daughter_name}")
            return daughter_cell

        return None

    def undergo_apoptosis(self, trigger: str = "natural"):
        """Initiate programmed cell death."""
        if not self.apoptotic:
            self.apoptotic = True
            self.is_active = False
            self.functional_capacity = 0.0

            print(f"Cell {self.name} undergoing apoptosis due to {trigger}")

            # Release damage-associated molecular patterns (DAMPs) if damaged
            if self.health < 50:
                self.inflammation_markers = min(1.0, self.inflammation_markers + 0.3)

    def respond_to_stress(self, stress_type: str, stress_level: float):
        """Respond to various cellular stresses."""
        stress_resistance_factor = self.stress_resistance

        if stress_type == "oxidative":
            # Oxidative stress
            stress_damage = stress_level * (1.0 - stress_resistance_factor)
            self.oxidative_stress = min(1.0, self.oxidative_stress + stress_damage)
            self.damage(stress_damage * 10)

        elif stress_type == "hypoxic":
            # Oxygen deficiency
            if stress_level > 0.5:
                self.functional_capacity *= 1.0 - stress_level * 0.3
                self.damage(stress_level * 15)

        elif stress_type == "toxic":
            # Toxic substance exposure
            toxicity_damage = stress_level * self.toxin_sensitivity
            self.damage(toxicity_damage * 20)
            self.inflammation_markers = min(
                1.0, self.inflammation_markers + toxicity_damage * 0.2
            )

        elif stress_type == "mechanical":
            # Physical stress
            mechanical_damage = stress_level * (1.0 - stress_resistance_factor)
            self.damage(mechanical_damage * 12)

        elif stress_type == "thermal":
            # Temperature stress
            thermal_damage = stress_level * (1.0 - stress_resistance_factor * 0.5)
            self.damage(thermal_damage * 18)

        # Trigger apoptosis if stress is too high
        if self.oxidative_stress > 0.8 or self.health < 20 or stress_level > 0.9:
            self.undergo_apoptosis(f"{stress_type}_stress")

    def age_cell(self, days: int = 1):
        """Age the cell by specified number of days."""
        self.cell_age += days

        # Natural aging effects
        aging_factor = self.cell_age / self.lifespan_days

        if aging_factor > 1.0:
            # Cell exceeded its natural lifespan
            self.undergo_apoptosis("aging")
        else:
            # Gradual decline with age
            age_related_decline = aging_factor * 0.1
            self.functional_capacity = max(
                0.3, self.functional_capacity - age_related_decline * 0.01
            )
            self.regeneration_potential = max(
                0.0, self.regeneration_potential - age_related_decline * 0.005
            )
            self.stress_resistance = max(
                0.2, self.stress_resistance - age_related_decline * 0.003
            )

            # Increase oxidative stress with age
            self.oxidative_stress = min(
                1.0, self.oxidative_stress + aging_factor * 0.001
            )

            # Check for senescence
            if aging_factor > 0.8 and not self.senescent:
                self.senescent = True
                self.regeneration_potential *= 0.1
                self.functional_capacity *= 0.7

    def get_cell_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the organ cell."""
        return {
            "name": self.name,
            "organ_type": self.organ_type,
            "cell_subtype": self.cell_subtype,
            "health": self.health,
            "is_active": self.is_active,
            "functional_capacity": self.functional_capacity,
            "metabolic_activity": self.metabolic_activity,
            "age_days": self.cell_age,
            "division_count": self.division_count,
            "senescent": self.senescent,
            "apoptotic": self.apoptotic,
            "oxidative_stress": self.oxidative_stress,
            "inflammation_markers": self.inflammation_markers,
            "specialization_level": self.specialization_level,
            "stress_resistance": self.stress_resistance,
            "regeneration_potential": self.regeneration_potential,
        }

    def describe(self) -> str:
        """Provide a detailed description of the organ cell."""
        base_description = super().describe()
        status = self.get_cell_status()

        additional_info = [
            f"Organ Type: {self.organ_type.capitalize()}",
            f"Cell Subtype: {self.cell_subtype.replace('_', ' ').title()}",
            f"Functional Capacity: {status['functional_capacity']:.1%}",
            f"Metabolic Activity: {status['metabolic_activity']:.2f}",
            f"Age: {status['age_days']} days",
            f"Divisions: {status['division_count']}/{self.max_divisions}",
            f"Oxidative Stress: {status['oxidative_stress']:.2f}",
            f"Specialization: {status['specialization_level']:.1%}",
            f"Status: {'Active' if status['is_active'] else 'Inactive'}",
        ]

        if status["senescent"]:
            additional_info.append("Status: SENESCENT")
        if status["apoptotic"]:
            additional_info.append("Status: APOPTOTIC")

        return f"{base_description}\n" + "\n".join(additional_info)
