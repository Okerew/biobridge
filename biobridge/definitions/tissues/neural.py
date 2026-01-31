from typing import Optional, List, Dict
from biobridge.blocks.tissue import Tissue
from biobridge.definitions.cells.neuron_cell import Neuron
import random
import math


class NeuralTissue(Tissue):
    def __init__(
        self,
        name: str,
        tissue_type: str = "nervous",
        cells: Optional[List[Neuron]] = None,
        cancer_risk: float = 0.0001,
        mutation_rate: float = 0.01,
        neural_density: float = 1.0,
        synaptic_connectivity: float = 0.7,
        myelination_percentage: float = 0.5,
        vascularization: float = 0.8
    ):
        super().__init__(
            name=name,
            tissue_type=tissue_type,
            cells=cells or [],
            cancer_risk=cancer_risk,
            mutation_rate=mutation_rate
        )
        
        self.neural_density = neural_density
        self.synaptic_connectivity = synaptic_connectivity
        self.myelination_percentage = myelination_percentage
        self.vascularization = vascularization
        self.glial_to_neuron_ratio = 1.5
        self.blood_brain_barrier_integrity = 100.0
        self.extracellular_matrix_density = 0.3
        self.interstitial_fluid_volume = 0.2
        self.astrocyte_density = 0.4
        self.oligodendrocyte_density = 0.2
        self.microglia_density = 0.1
        self.neural_progenitor_cells = 0.01
        self.tissue_stiffness = 0.5
        self.glucose_metabolism_rate = 1.0
        self.oxygen_consumption_rate = 1.2
        self.neurotrophic_factor_concentration = 1.0

    def calculate_total_synapses(self) -> int:
        total = 0
        for cell in self.cells:
            if isinstance(cell, Neuron):
                total += cell.synapse_count
        return total

    def calculate_average_conduction_velocity(self) -> float:
        if not self.cells:
            return 0.0
        
        velocities = []
        for cell in self.cells:
            if isinstance(cell, Neuron):
                velocities.append(cell.calculate_conduction_velocity())
        
        return sum(velocities) / len(velocities) if velocities else 0.0

    def calculate_synaptic_density(self) -> float:
        total_synapses = self.calculate_total_synapses()
        
        total_volume = 0
        for cell in self.cells:
            if isinstance(cell, Neuron):
                total_volume += cell.calculate_total_neuron_volume()
        
        if total_volume > 0:
            return total_synapses / total_volume
        return 0.0

    def calculate_myelination_coverage(self) -> Dict[str, float]:
        myelinated_length = 0
        total_axon_length = 0
        
        for cell in self.cells:
            if isinstance(cell, Neuron):
                total_axon_length += cell.axon_length
                if cell.myelin_thickness > 0:
                    myelinated_length += cell.axon_length
        
        if total_axon_length > 0:
            coverage = myelinated_length / total_axon_length
        else:
            coverage = 0.0
        
        return {
            "myelinated_length": myelinated_length,
            "total_axon_length": total_axon_length,
            "coverage_percentage": coverage * 100,
            "average_g_ratio": 0.6
        }

    def propagate_wave(
        self,
        initiation_site: int,
        wave_type: str = "excitatory",
        intensity: float = 1.0
    ) -> Dict[str, any]:
        if not self.cells or initiation_site >= len(self.cells):
            return {"error": "Invalid initiation site"}
        
        wave_speed = self.calculate_average_conduction_velocity()
        
        affected_neurons = []
        propagation_pattern = []
        
        start_neuron = self.cells[initiation_site]
        if not isinstance(start_neuron, Neuron):
            return {"error": "Initiation site is not a neuron"}
        
        visited = set()
        queue = [(initiation_site, 0, intensity)]
        
        while queue:
            idx, distance, current_intensity = queue.pop(0)
            
            if idx in visited or current_intensity < 0.1:
                continue
            
            visited.add(idx)
            neuron = self.cells[idx]
            
            if isinstance(neuron, Neuron):
                affected_neurons.append(idx)
                propagation_pattern.append({
                    "neuron_id": idx,
                    "distance": distance,
                    "intensity": current_intensity,
                    "arrival_time": distance / wave_speed if wave_speed > 0 else 0
                })
                
                connectivity = self.synaptic_connectivity
                attenuation = 0.95 if wave_type == "excitatory" else 0.9
                new_intensity = current_intensity * attenuation
                
                max_connections = int(neuron.synapse_count * connectivity * 0.001)
                
                for _ in range(min(max_connections, len(self.cells) - len(visited))):
                    next_idx = random.randint(0, len(self.cells) - 1)
                    if next_idx not in visited:
                        queue.append((next_idx, 
                                    distance + 1, 
                                    new_intensity))
        
        return {
            "wave_type": wave_type,
            "initiation_site": initiation_site,
            "affected_neuron_count": len(affected_neurons),
            "affected_neurons": affected_neurons,
            "propagation_pattern": propagation_pattern,
            "max_distance": max((p["distance"] for p in propagation_pattern), 
                               default=0),
            "average_intensity": (sum(p["intensity"] 
                                    for p in propagation_pattern) / 
                                len(propagation_pattern) 
                                if propagation_pattern else 0)
        }

    def simulate_oscillatory_activity(
        self,
        frequency: float = 10.0,
        duration: int = 100,
        synchronization: float = 0.5
    ) -> Dict[str, any]:
        if not self.cells:
            return {"error": "No neurons in tissue"}
        
        period = 1000.0 / frequency
        time_points = []
        amplitude_data = []
        
        participating_neurons = int(len(self.cells) * synchronization)
        
        for t in range(duration):
            phase = (t % period) / period * 2 * math.pi
            
            amplitude = 0
            for i in range(participating_neurons):
                neuron = self.cells[i]
                if isinstance(neuron, Neuron):
                    individual_phase = phase + random.uniform(-0.5, 0.5)
                    contribution = math.sin(individual_phase)
                    amplitude += contribution * (neuron.health / 100)
            
            amplitude /= participating_neurons if participating_neurons > 0 else 1
            
            time_points.append(t)
            amplitude_data.append(amplitude)
        
        peak_frequency = frequency
        coherence = synchronization
        
        return {
            "frequency": frequency,
            "duration": duration,
            "time_points": time_points,
            "amplitude": amplitude_data,
            "participating_neurons": participating_neurons,
            "peak_frequency": peak_frequency,
            "coherence": coherence,
            "power": sum(a**2 for a in amplitude_data) / len(amplitude_data)
        }

    def calculate_network_connectivity(self) -> Dict[str, float]:
        if not self.cells:
            return {"error": "No neurons"}
        
        neuron_count = sum(1 for c in self.cells if isinstance(c, Neuron))
        
        if neuron_count == 0:
            return {"error": "No neurons"}
        
        total_synapses = self.calculate_total_synapses()
        
        max_possible = neuron_count * (neuron_count - 1)
        actual_connectivity = (total_synapses / max_possible 
                              if max_possible > 0 else 0)
        
        clustering_coefficient = self.synaptic_connectivity ** 2
        
        path_length = math.log(neuron_count) if neuron_count > 1 else 1
        
        small_world_index = clustering_coefficient / path_length if path_length > 0 else 0
        
        return {
            "neuron_count": neuron_count,
            "total_synapses": total_synapses,
            "connectivity_density": actual_connectivity,
            "clustering_coefficient": clustering_coefficient,
            "characteristic_path_length": path_length,
            "small_world_index": small_world_index
        }

    def assess_white_matter_integrity(self) -> Dict[str, float]:
        myelinated_neurons = 0
        total_myelin_thickness = 0
        axon_integrity = 0
        
        for cell in self.cells:
            if isinstance(cell, Neuron):
                if cell.myelin_thickness > 0:
                    myelinated_neurons += 1
                    total_myelin_thickness += cell.myelin_thickness
                    axon_integrity += cell.structural_integrity
        
        if myelinated_neurons > 0:
            avg_myelin = total_myelin_thickness / myelinated_neurons
            avg_integrity = axon_integrity / myelinated_neurons
        else:
            avg_myelin = 0
            avg_integrity = 0
        
        fractional_anisotropy = (self.myelination_percentage * 
                                avg_integrity / 100 * 0.8)
        
        mean_diffusivity = 0.8 - (fractional_anisotropy * 0.3)
        
        return {
            "myelinated_neuron_count": myelinated_neurons,
            "average_myelin_thickness": avg_myelin,
            "axonal_integrity": avg_integrity,
            "fractional_anisotropy": min(1.0, fractional_anisotropy),
            "mean_diffusivity": mean_diffusivity,
            "white_matter_volume": myelinated_neurons * 100
        }

    def calculate_gray_matter_density(self) -> Dict[str, float]:
        total_soma_volume = 0
        total_dendrite_volume = 0
        synapse_density = 0
        
        for cell in self.cells:
            if isinstance(cell, Neuron):
                total_soma_volume += cell.calculate_soma_volume()
                dendrite_vol = cell.dendrite_count * 10 * cell.dendrite_branch_density
                total_dendrite_volume += dendrite_vol
        
        synapse_density = self.calculate_synaptic_density()
        
        neuropil_volume = total_dendrite_volume * 1.5
        
        total_gray_matter = total_soma_volume + total_dendrite_volume + neuropil_volume
        
        return {
            "soma_volume": total_soma_volume,
            "dendrite_volume": total_dendrite_volume,
            "neuropil_volume": neuropil_volume,
            "total_gray_matter_volume": total_gray_matter,
            "synaptic_density": synapse_density,
            "neuronal_density": len(self.cells) / total_gray_matter if total_gray_matter > 0 else 0
        }

    def neurotransmitter_system_analysis(self) -> Dict[str, any]:
        neurotransmitter_profile = {}
        
        for cell in self.cells:
            if isinstance(cell, Neuron):
                for nt in cell.neurotransmitter_types:
                    if nt not in neurotransmitter_profile:
                        neurotransmitter_profile[nt] = {
                            "neuron_count": 0,
                            "total_content": 0,
                            "vesicle_count": 0
                        }
                    
                    neurotransmitter_profile[nt]["neuron_count"] += 1
                    nt_content = cell.calculate_neurotransmitter_content()
                    neurotransmitter_profile[nt]["total_content"] += nt_content.get(nt, 0)
                    neurotransmitter_profile[nt]["vesicle_count"] += (
                        cell.neurotransmitter_vesicles
                    )
        
        dominant_system = max(neurotransmitter_profile.items(), 
                             key=lambda x: x[1]["neuron_count"])[0] if neurotransmitter_profile else "none"
        
        return {
            "neurotransmitter_systems": neurotransmitter_profile,
            "dominant_system": dominant_system,
            "system_diversity": len(neurotransmitter_profile)
        }

    def glial_cell_distribution(self) -> Dict[str, float]:
        neuron_count = sum(1 for c in self.cells if isinstance(c, Neuron))
        
        estimated_glia = int(neuron_count * self.glial_to_neuron_ratio)
        
        astrocytes = int(estimated_glia * self.astrocyte_density)
        oligodendrocytes = int(estimated_glia * self.oligodendrocyte_density)
        microglia = int(estimated_glia * self.microglia_density)
        
        return {
            "total_glial_cells": estimated_glia,
            "astrocytes": astrocytes,
            "oligodendrocytes": oligodendrocytes,
            "microglia": microglia,
            "glial_to_neuron_ratio": self.glial_to_neuron_ratio,
            "astrocyte_coverage": astrocytes * 1000
        }

    def blood_brain_barrier_assessment(self) -> Dict[str, float]:
        permeability = 100 - self.blood_brain_barrier_integrity
        
        tight_junction_integrity = self.blood_brain_barrier_integrity / 100
        
        vascular_density = self.vascularization * 1000
        
        return {
            "bbb_integrity": self.blood_brain_barrier_integrity,
            "permeability": permeability,
            "tight_junction_integrity": tight_junction_integrity,
            "vascular_density": vascular_density,
            "astrocytic_endfeet_coverage": self.astrocyte_density * 95
        }

    def neural_tissue_metabolism(self) -> Dict[str, float]:
        total_atp_demand = 0
        glucose_consumption = 0
        oxygen_consumption = 0
        
        for cell in self.cells:
            if isinstance(cell, Neuron):
                metabolic_data = cell.neuron_metabolic_rate()
                total_atp_demand += metabolic_data["atp_consumption"]
        
        neuron_count = sum(1 for c in self.cells if isinstance(c, Neuron))
        glucose_consumption = neuron_count * 5.0 * self.glucose_metabolism_rate
        oxygen_consumption = neuron_count * 3.5 * self.oxygen_consumption_rate
        
        lactate_production = glucose_consumption * 0.1
        
        return {
            "total_atp_demand": total_atp_demand,
            "glucose_consumption": glucose_consumption,
            "oxygen_consumption": oxygen_consumption,
            "lactate_production": lactate_production,
            "cmro2": oxygen_consumption / neuron_count if neuron_count > 0 else 0
        }

    def neuroplasticity_assessment(self) -> Dict[str, float]:
        total_spine_turnover = 0
        total_synapse_formation = 0
        
        for cell in self.cells:
            if isinstance(cell, Neuron):
                turnover = cell.dendritic_spine_turnover()
                total_spine_turnover += turnover["net_change"]
                total_synapse_formation += turnover["formation_rate"]
        
        ltp_capacity = self.synaptic_connectivity * (self.get_average_cell_health() / 100)
        
        structural_plasticity = total_spine_turnover / len(self.cells) if self.cells else 0
        
        return {
            "spine_turnover_rate": total_spine_turnover,
            "synapse_formation_rate": total_synapse_formation,
            "ltp_capacity": ltp_capacity,
            "structural_plasticity_index": structural_plasticity,
            "neurotrophic_support": self.neurotrophic_factor_concentration
        }

    def axonal_transport_efficiency(self) -> Dict[str, float]:
        fast_transport_rates = []
        slow_transport_rates = []
        
        for cell in self.cells:
            if isinstance(cell, Neuron):
                fast_transport_rates.append(
                    cell.axonal_transport_rate("fast")
                )
                slow_transport_rates.append(
                    cell.axonal_transport_rate("slow")
                )
        
        avg_fast = (sum(fast_transport_rates) / len(fast_transport_rates) 
                   if fast_transport_rates else 0)
        avg_slow = (sum(slow_transport_rates) / len(slow_transport_rates) 
                   if slow_transport_rates else 0)
        
        transport_impairment = 1 - (self.get_average_cell_health() / 100)
        
        return {
            "average_fast_transport": avg_fast,
            "average_slow_transport": avg_slow,
            "transport_efficiency": 1 - transport_impairment,
            "axonal_swelling_index": transport_impairment * 0.5
        }

    def neuroinflammation_markers(self) -> Dict[str, float]:
        activated_microglia = (self.microglia_density * 
                              (1 - self.get_average_cell_health() / 100))
        
        reactive_astrocytes = (self.astrocyte_density * 
                              (1 - self.get_average_cell_health() / 100) * 0.7)
        
        cytokine_level = activated_microglia * 10
        
        bbb_disruption = 100 - self.blood_brain_barrier_integrity
        
        return {
            "activated_microglia": activated_microglia,
            "reactive_astrocytes": reactive_astrocytes,
            "pro_inflammatory_cytokines": cytokine_level,
            "bbb_disruption": bbb_disruption,
            "inflammation_index": (activated_microglia + reactive_astrocytes + 
                                  cytokine_level / 10) / 3
        }

    def neurodegenerative_pathology(self) -> Dict[str, any]:
        degeneration_scores = []
        tau_pathology = 0
        amyloid_burden = 0
        synaptic_loss = 0
        
        for cell in self.cells:
            if isinstance(cell, Neuron):
                markers = cell.assess_neurodegeneration_markers()
                degeneration_scores.append(markers["overall_degeneration"])
                tau_pathology += markers["tau_pathology"]
                amyloid_burden += markers["amyloid_burden"]
                synaptic_loss += markers["synaptic_loss"]
        
        neuron_count = sum(1 for c in self.cells if isinstance(c, Neuron))
        
        if neuron_count > 0:
            avg_degeneration = sum(degeneration_scores) / neuron_count
            avg_tau = tau_pathology / neuron_count
            avg_amyloid = amyloid_burden / neuron_count
            avg_synaptic_loss = synaptic_loss / neuron_count
        else:
            avg_degeneration = avg_tau = avg_amyloid = avg_synaptic_loss = 0
        
        neuronal_loss_rate = (1 - neuron_count / max(1000, neuron_count)) * 100
        
        return {
            "overall_degeneration": avg_degeneration,
            "tau_pathology": avg_tau,
            "amyloid_pathology": avg_amyloid,
            "synaptic_loss": avg_synaptic_loss,
            "neuronal_loss_percentage": neuronal_loss_rate,
            "tissue_atrophy": avg_degeneration * 50
        }

    def extracellular_matrix_composition(self) -> Dict[str, float]:
        return {
            "hyaluronic_acid": self.extracellular_matrix_density * 0.4,
            "proteoglycans": self.extracellular_matrix_density * 0.3,
            "tenascins": self.extracellular_matrix_density * 0.2,
            "laminins": self.extracellular_matrix_density * 0.1,
            "matrix_density": self.extracellular_matrix_density,
            "interstitial_fluid": self.interstitial_fluid_volume
        }

    def neural_progenitor_activity(self) -> Dict[str, any]:
        total_progenitors = int(len(self.cells) * self.neural_progenitor_cells)
        
        proliferation_rate = (self.neurotrophic_factor_concentration * 
                             (self.get_average_cell_health() / 100) * 0.1)
        
        differentiation_rate = proliferation_rate * 0.7
        
        new_neurons = int(total_progenitors * differentiation_rate)
        
        return {
            "progenitor_pool": total_progenitors,
            "proliferation_rate": proliferation_rate,
            "differentiation_rate": differentiation_rate,
            "neurogenesis_rate": new_neurons,
            "niche_health": self.get_average_cell_health()
        }

    def tissue_biomechanics(self) -> Dict[str, float]:
        elastic_modulus = self.tissue_stiffness * 1000
        
        shear_modulus = elastic_modulus * 0.3
        
        viscosity = self.tissue_stiffness * 50
        
        return {
            "elastic_modulus_pa": elastic_modulus,
            "shear_modulus_pa": shear_modulus,
            "viscosity": viscosity,
            "tissue_stiffness": self.tissue_stiffness,
            "compliance": 1 / self.tissue_stiffness if self.tissue_stiffness > 0 else 1
        }

    def comprehensive_neural_assessment(self) -> Dict[str, any]:
        return {
            "morphology": {
                "gray_matter": self.calculate_gray_matter_density(),
                "white_matter": self.assess_white_matter_integrity(),
                "myelination": self.calculate_myelination_coverage()
            },
            "connectivity": {
                "network": self.calculate_network_connectivity(),
                "synaptic_density": self.calculate_synaptic_density(),
                "conduction_velocity": self.calculate_average_conduction_velocity()
            },
            "metabolism": self.neural_tissue_metabolism(),
            "cellular_health": {
                "average_health": self.get_average_cell_health(),
                "degeneration": self.neurodegenerative_pathology(),
                "inflammation": self.neuroinflammation_markers()
            },
            "glial_support": self.glial_cell_distribution(),
            "vascular": {
                "bbb": self.blood_brain_barrier_assessment(),
                "vascularization": self.vascularization
            },
            "plasticity": self.neuroplasticity_assessment(),
            "neurotransmitters": self.neurotransmitter_system_analysis()
        }
