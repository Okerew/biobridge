import random
from typing import List, Optional, Dict
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
                    self.apply_mutation(new_cell)

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

    def angiogenesis(self, oxygen_level: float = 0.5) -> Dict[str, int]:
        """
        Simulate blood vessel formation in response to hypoxia.
        """
        if oxygen_level > 0.7:
            return {'new_vessels': 0, 'vegf_production': 0}
        
        hypoxic_cells = [cell for cell in self.cells if cell.health < 60]
        vegf_production = len(hypoxic_cells)
        
        vessel_formation_rate = max(0, (0.7 - oxygen_level) * 10)
        new_vessels = int(vessel_formation_rate * len(hypoxic_cells) * 0.1)
        
        for cell in hypoxic_cells:
            cell.health = min(100, cell.health + 15)
        
        return {'new_vessels': new_vessels, 'vegf_production': vegf_production}

    def immune_response(self, pathogen_count: int, pathogen_type: str = "bacteria") -> Dict[str, any]:
        """
        Simulate tissue immune response to pathogens.
        """
        if pathogen_count <= 0:
            return {'immune_cells_recruited': 0, 'inflammation_level': 0, 'pathogen_cleared': 0}
        
        inflammation_level = min(10, pathogen_count * 0.5)
        immune_cells_recruited = int(pathogen_count * 1.5)
        
        effectiveness = 0.7 if pathogen_type == "bacteria" else 0.5 if pathogen_type == "virus" else 0.3
        pathogen_cleared = int(pathogen_count * effectiveness)
        
        collateral_damage = int(immune_cells_recruited * 0.1)
        damaged_cells = min(collateral_damage, len(self.cells))
        
        for i in range(damaged_cells):
            if i < len(self.cells):
                self.cells[i].health = max(0, self.cells[i].health - 10)
        
        return {
            'immune_cells_recruited': immune_cells_recruited,
            'inflammation_level': inflammation_level,
            'pathogen_cleared': pathogen_cleared,
            'collateral_damage': collateral_damage
        }

    def fibrosis_progression(self, injury_severity: float = 0.3) -> Dict[str, float]:
        """
        Simulate fibrotic tissue formation after chronic injury.
        """
        if injury_severity < 0.2:
            return {'collagen_deposition': 0, 'tissue_stiffness': 0, 'functional_loss': 0}
        
        collagen_deposition = injury_severity * len(self.cells) * 0.05
        tissue_stiffness = min(1.0, injury_severity * 2)
        functional_loss = tissue_stiffness * 0.3
        
        fibrotic_cells = int(len(self.cells) * injury_severity * 0.2)
        for i in range(min(fibrotic_cells, len(self.cells))):
            self.cells[i].metabolism_rate *= (1 - functional_loss)
            self.cells[i].growth_rate *= (1 - tissue_stiffness * 0.5)
        
        return {
            'collagen_deposition': collagen_deposition,
            'tissue_stiffness': tissue_stiffness,
            'functional_loss': functional_loss
        }

    def stem_cell_activation(self, damage_level: float = 0.4) -> Dict[str, int]:
        """
        Activate stem cells for tissue repair and regeneration.
        """
        if damage_level < 0.2:
            return {'stem_cells_activated': 0, 'new_cells_generated': 0}
        
        stem_cell_pool = max(1, len(self.cells) // 20)
        
        activation_rate = min(1.0, damage_level * 2)
        stem_cells_activated = int(stem_cell_pool * activation_rate)
        
        new_cells_generated = stem_cells_activated * 3
        
        for _ in range(new_cells_generated):
            new_cell = Cell(f"Regenerated_Cell_{random.randint(1000, 9999)}", 
                           self.tissue_type)
            new_cell.health = random.uniform(80, 100)
            new_cell.age = 0
            self.add_cell(new_cell)
        
        return {
            'stem_cells_activated': stem_cells_activated,
            'new_cells_generated': new_cells_generated
        }

    def extracellular_matrix_remodeling(self) -> Dict[str, float]:
        """
        Simulate ECM remodeling processes.
        """
        avg_cell_age = sum(cell.age for cell in self.cells) / len(self.cells) if self.cells else 0
        remodeling_rate = min(1.0, avg_cell_age / 500)
        
        collagenase_activity = remodeling_rate * 0.8
        new_collagen_synthesis = (1 - remodeling_rate) * 0.6
        elastin_degradation = remodeling_rate * 0.4
        
        matrix_turnover = (collagenase_activity + new_collagen_synthesis) / 2
        
        for cell in self.cells:
            cell.structural_integrity *= (1 - elastin_degradation * 0.1)
            cell.structural_integrity = max(0, cell.structural_integrity)
        
        return {
            'collagenase_activity': collagenase_activity,
            'collagen_synthesis': new_collagen_synthesis,
            'elastin_degradation': elastin_degradation,
            'matrix_turnover_rate': matrix_turnover
        }

    def tissue_oxygenation(self, blood_flow: float = 1.0, hemoglobin: float = 1.0) -> Dict[str, float]:
        """
        Calculate and manage tissue oxygenation levels.
        """
        base_oxygen_delivery = blood_flow * hemoglobin * 1.34
        tissue_oxygen_consumption = len(self.cells) * 0.25
        
        oxygen_extraction_ratio = min(1.0, tissue_oxygen_consumption / base_oxygen_delivery)
        tissue_po2 = base_oxygen_delivery * (1 - oxygen_extraction_ratio) * 40
        
        hypoxic_threshold = 20
        hypoxic_cells = 0
        
        for cell in self.cells:
            if tissue_po2 < hypoxic_threshold:
                cell.metabolism_rate *= 0.7
                cell.health = max(0, cell.health - 2)
                hypoxic_cells += 1
            elif tissue_po2 > 80:
                cell.metabolism_rate *= 1.1
                cell.health = min(100, cell.health + 1)
        
        return {
            'tissue_po2': tissue_po2,
            'oxygen_extraction_ratio': oxygen_extraction_ratio,
            'hypoxic_cells': hypoxic_cells,
            'oxygen_delivery': base_oxygen_delivery
        }

    def hormonal_regulation(self, hormones: Dict[str, float]) -> Dict[str, str]:
        """
        Respond to hormonal signals affecting tissue function.
        """
        responses = {}
        
        if 'growth_hormone' in hormones:
            gh_level = hormones['growth_hormone']
            self.growth_rate *= (1 + gh_level * 0.3)
            for cell in self.cells:
                cell.growth_rate *= (1 + gh_level * 0.2)
            responses['growth_hormone'] = f"Increased growth rate by {gh_level * 30:.1f}%"
        
        if 'cortisol' in hormones:
            cortisol_level = hormones['cortisol']
            for cell in self.cells:
                cell.health = max(0, cell.health - cortisol_level * 5)
                cell.metabolism_rate *= (1 - cortisol_level * 0.1)
            responses['cortisol'] = f"Stress response - reduced metabolism"
        
        if 'insulin' in hormones:
            insulin_level = hormones['insulin']
            for cell in self.cells:
                glucose_uptake = insulin_level * 1.5
                cell.health = min(100, cell.health + glucose_uptake)
            responses['insulin'] = f"Enhanced glucose uptake"
        
        if 'thyroid_hormone' in hormones:
            th_level = hormones['thyroid_hormone']
            for cell in self.cells:
                cell.metabolism_rate *= (1 + th_level * 0.4)
            responses['thyroid_hormone'] = f"Metabolic rate adjustment"
        
        return responses

    def mechanical_stress_response(self, stress_type: str, magnitude: float) -> Dict[str, any]:
        """
        Respond to mechanical forces applied to tissue.
        """
        if magnitude <= 0:
            return {'adaptation': 'none', 'damage': 0}
        
        if stress_type == "tension":
            if magnitude < 0.5:
                for cell in self.cells:
                    cell.structural_integrity *= (1 + magnitude * 0.1)
                return {'adaptation': 'strengthening', 'damage': 0}
            else:
                damage = int(len(self.cells) * (magnitude - 0.5) * 0.2)
                for i in range(min(damage, len(self.cells))):
                    self.cells[i].health = max(0, self.cells[i].health - 20)
                return {'adaptation': 'damage', 'damage': damage}
        
        elif stress_type == "compression":
            if magnitude < 0.7:
                self.growth_rate *= (1 - magnitude * 0.3)
                return {'adaptation': 'reduced_growth', 'damage': 0}
            else:
                necrotic_cells = int(len(self.cells) * (magnitude - 0.7) * 0.3)
                self.cells = self.cells[:-necrotic_cells]
                return {'adaptation': 'necrosis', 'damage': necrotic_cells}
        
        elif stress_type == "shear":
            cell_alignment = min(1.0, magnitude)
            for cell in self.cells:
                cell.structural_integrity *= (1 + cell_alignment * 0.05)
            return {'adaptation': 'cell_alignment', 'damage': 0}
        
        return {'adaptation': 'unknown', 'damage': 0}

    def neurotrophic_signaling(self, signal_strength: float = 0.5) -> Dict[str, any]:
        """
        Process neurotrophic signals affecting tissue innervation.
        """
        if self.tissue_type not in ["nervous", "muscle", "epithelial"]:
            return {'response': 'tissue_not_responsive'}
        
        innervation_density = signal_strength * 10
        
        responses = {
            'innervation_density': innervation_density,
            'growth_cone_guidance': signal_strength > 0.3,
            'synaptic_plasticity': signal_strength > 0.6
        }
        
        if signal_strength > 0.4:
            for cell in self.cells:
                cell.metabolism_rate *= (1 + signal_strength * 0.2)
                if hasattr(cell, 'neurotransmitter_sensitivity'):
                    cell.neurotransmitter_sensitivity *= (1 + signal_strength * 0.3)
        
        if signal_strength < 0.2:
            denervation_effects = int(len(self.cells) * 0.1)
            for i in range(min(denervation_effects, len(self.cells))):
                self.cells[i].health = max(0, self.cells[i].health - 5)
            responses['denervation'] = denervation_effects
        
        return responses

    def metabolic_coupling(self, metabolites: Dict[str, float]) -> Dict[str, float]:
        """
        Handle metabolic coupling between cells in tissue.
        """
        coupling_strength = len(self.cells) / 100
        metabolite_exchange = {}
        
        for metabolite, concentration in metabolites.items():
            if metabolite == "glucose":
                glucose_sharing = concentration * coupling_strength * 0.8
                for cell in self.cells:
                    cell.health = min(100, cell.health + glucose_sharing * 2)
                metabolite_exchange["glucose_shared"] = glucose_sharing
            
            elif metabolite == "lactate":
                if concentration > 2.0:
                    acidosis_effect = (concentration - 2.0) * 0.1
                    for cell in self.cells:
                        cell.ph = max(6.5, cell.ph - acidosis_effect)
                        cell.health = max(0, cell.health - acidosis_effect * 10)
                    metabolite_exchange["acidosis_level"] = acidosis_effect
            
            elif metabolite == "atp":
                energy_distribution = concentration * coupling_strength
                for cell in self.cells:
                    cell.metabolism_rate *= (1 + energy_distribution * 0.1)
                metabolite_exchange["energy_shared"] = energy_distribution
            
            elif metabolite == "calcium":
                if concentration > 1.0:
                    calcium_wave = (concentration - 1.0) * coupling_strength
                    synchronized_cells = int(len(self.cells) * calcium_wave)
                    metabolite_exchange["synchronized_cells"] = synchronized_cells
        
        return metabolite_exchange

    def tissue_aging(self, age_acceleration: float = 1.0) -> Dict[str, any]:
        """
        Simulate tissue aging processes.
        """
        aging_effects = {
            'senescent_cells': 0,
            'collagen_crosslinking': 0,
            'oxidative_damage': 0
        }
        
        for cell in self.cells:
            cell.age += age_acceleration
            
            if cell.age > 600:
                senescence_probability = min(0.8, (cell.age - 600) / 400)
                if random.random() < senescence_probability:
                    cell.growth_rate *= 0.1
                    cell.metabolism_rate *= 0.7
                    aging_effects['senescent_cells'] += 1
            
            oxidative_damage = age_acceleration * random.uniform(0.5, 1.5)
            cell.health = max(0, cell.health - oxidative_damage)
            aging_effects['oxidative_damage'] += oxidative_damage
        
        tissue_stiffness = min(2.0, age_acceleration * len(self.cells) * 0.001)
        aging_effects['collagen_crosslinking'] = tissue_stiffness
        
        return aging_effects

    def tissue_pH_regulation(self, acid_load: float = 0.0) -> Dict[str, float]:
        """
        Regulate tissue pH through buffering systems.
        """
        if not self.cells:
            return {'average_pH': 7.0, 'buffering_capacity': 0}
        
        current_avg_ph = sum(cell.ph for cell in self.cells) / len(self.cells)
        target_ph = 7.4
        
        ph_deviation = abs(current_avg_ph - target_ph)
        buffering_capacity = max(0, 1 - ph_deviation / 2)
        
        bicarbonate_buffering = min(0.2, acid_load * buffering_capacity)
        phosphate_buffering = min(0.1, acid_load * buffering_capacity * 0.5)
        protein_buffering = min(0.15, acid_load * buffering_capacity * 0.7)
        
        total_buffering = bicarbonate_buffering + phosphate_buffering + protein_buffering
        
        ph_correction = min(0.3, total_buffering)
        
        for cell in self.cells:
            if cell.ph < target_ph:
                cell.ph = min(target_ph, cell.ph + ph_correction)
            elif cell.ph > target_ph:
                cell.ph = max(target_ph, cell.ph - ph_correction)
        
        final_avg_ph = sum(cell.ph for cell in self.cells) / len(self.cells)
        
        return {
            'average_pH': final_avg_ph,
            'buffering_capacity': buffering_capacity,
            'bicarbonate_buffering': bicarbonate_buffering,
            'phosphate_buffering': phosphate_buffering,
            'protein_buffering': protein_buffering
        }

    def calculate_tissue_fitness(self) -> Dict[str, float]:
        """
        Calculate comprehensive tissue health and functionality metrics.
        """
        if not self.cells:
            return {'overall_fitness': 0, 'cell_viability': 0, 'functional_capacity': 0}
        
        cell_viabilities = [cell.calculate_fitness() if hasattr(cell, 'calculate_fitness') 
                           else cell.health / 100 for cell in self.cells]
        avg_cell_viability = sum(cell_viabilities) / len(cell_viabilities)
        
        structural_integrity = sum(cell.structural_integrity for cell in self.cells) / len(self.cells)
        metabolic_activity = sum(cell.metabolism_rate for cell in self.cells) / len(self.cells)
        
        cell_density_score = min(1.0, len(self.cells) / 1000)
        age_penalty = max(0, 1 - (sum(cell.age for cell in self.cells) / len(self.cells)) / 1000)
        
        functional_capacity = (structural_integrity / 100 * 0.4 + 
                              metabolic_activity * 0.3 + 
                              cell_density_score * 0.2 + 
                              age_penalty * 0.1)
        
        overall_fitness = (avg_cell_viability * 0.5 + functional_capacity * 0.5)
        
        return {
            'overall_fitness': max(0, min(1, overall_fitness)),
            'cell_viability': avg_cell_viability,
            'functional_capacity': functional_capacity,
            'structural_integrity': structural_integrity / 100,
            'metabolic_activity': metabolic_activity,
            'age_factor': age_penalty
        }

    def __str__(self) -> str:
        """Return a string representation of the tissue."""
        return self.describe()
