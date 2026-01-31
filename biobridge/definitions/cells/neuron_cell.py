from typing import Optional, List, Dict
from biobridge.blocks.cell import Cell, DNA, Protein, Chromosome
import random
import math


class Neuron(Cell):
    def __init__(
        self,
        name: str,
        cell_type: str = "neuron",
        receptors: Optional[List[Protein]] = None,
        surface_proteins: Optional[List[Protein]] = None,
        dna: Optional['DNA'] = None,
        health: Optional[int] = None,
        age: Optional[int] = 0,
        metabolism_rate: Optional[float] = 1.2,
        ph: float = 7.0,
        osmolarity: float = 300.0,
        ion_concentrations: Optional[Dict[str, float]] = None,
        id: Optional[int] = None,
        chromosomes: Optional[List[Chromosome]] = None,
        structural_integrity: float = 100.0,
        mutation_count: Optional[int] = 0,
        growth_rate: Optional[float] = 0.1,
        repair_rate: Optional[float] = 0.8,
        max_divisions: Optional[int] = 0,
        soma_diameter: float = 20.0,
        axon_length: float = 1000.0,
        axon_diameter: float = 1.0,
        dendrite_count: int = 5,
        dendrite_branch_density: float = 0.7,
        myelin_thickness: float = 0.0,
        synapse_count: int = 1000,
        neurotransmitter_types: Optional[List[str]] = None
    ):
        neuron_ion_concentrations = ion_concentrations or {
            "Na+": 12.0,
            "K+": 140.0,
            "Cl-": 4.0,
            "Ca2+": 0.0001,
            "Mg2+": 0.5
        }
        
        super().__init__(
            name=name,
            cell_type=cell_type,
            receptors=receptors,
            surface_proteins=surface_proteins,
            dna=dna,
            health=health,
            age=age,
            metabolism_rate=metabolism_rate,
            ph=ph,
            osmolarity=osmolarity,
            ion_concentrations=neuron_ion_concentrations,
            id=id,
            chromosomes=chromosomes,
            structural_integrity=structural_integrity,
            mutation_count=mutation_count,
            growth_rate=growth_rate,
            repair_rate=repair_rate,
            max_divisions=max_divisions
        )
        
        self.soma_diameter = soma_diameter
        self.axon_length = axon_length
        self.axon_diameter = axon_diameter
        self.dendrite_count = dendrite_count
        self.dendrite_branch_density = dendrite_branch_density
        self.myelin_thickness = myelin_thickness
        self.synapse_count = synapse_count
        self.spine_density = 1.5
        self.neurotransmitter_types = neurotransmitter_types or ["glutamate"]
        self.resting_potential = -70.0
        self.neurotransmitter_vesicles = synapse_count * 200
        self.mitochondria_density = 0.15
        self.neurofilament_density = 1.0
        self.synaptic_vesicle_size = 40.0
        self.dendritic_spine_morphology = "mushroom"
        self.axon_initial_segment_length = 30.0
        self.nodes_of_ranvier_count = int(axon_length / 100) if myelin_thickness > 0 else 0

    def calculate_conduction_velocity(self) -> float:
        if self.myelin_thickness > 0:
            velocity = 6.0 * self.axon_diameter * (1 + self.myelin_thickness / 2)
        else:
            velocity = 0.5 * math.sqrt(self.axon_diameter)
        
        integrity_factor = self.structural_integrity / 100
        return velocity * integrity_factor

    def calculate_membrane_capacitance(self) -> float:
        soma_surface = 4 * math.pi * (self.soma_diameter / 2) ** 2
        axon_surface = math.pi * self.axon_diameter * self.axon_length
        dendrite_surface = self.dendrite_count * 50 * self.dendrite_branch_density
        
        total_surface = soma_surface + axon_surface + dendrite_surface
        
        base_capacitance = 1.0
        if self.myelin_thickness > 0:
            capacitance = base_capacitance / (1 + self.myelin_thickness * 10)
        else:
            capacitance = base_capacitance
        
        return total_surface * capacitance

    def calculate_input_resistance(self) -> float:
        soma_surface = 4 * math.pi * (self.soma_diameter / 2) ** 2
        
        base_conductance = soma_surface * 0.0001
        
        dendrite_conductance = (self.dendrite_count * 
                               self.dendrite_branch_density * 0.001)
        
        total_conductance = base_conductance + dendrite_conductance
        
        resistance = 1 / total_conductance if total_conductance > 0 else 1e6
        
        return resistance

    def calculate_synaptic_density(self) -> float:
        dendrite_surface = self.dendrite_count * 50 * self.dendrite_branch_density
        
        if dendrite_surface > 0:
            return self.synapse_count / dendrite_surface
        return 0.0

    def calculate_dendritic_arbor_complexity(self) -> Dict[str, float]:
        total_dendrite_length = self.dendrite_count * 100 * self.dendrite_branch_density
        
        branch_points = int(self.dendrite_count * self.dendrite_branch_density * 10)
        
        sholl_intersections = self.dendrite_count * (1 + self.dendrite_branch_density)
        
        return {
            "total_length": total_dendrite_length,
            "branch_points": branch_points,
            "sholl_intersections": sholl_intersections,
            "complexity_index": self.dendrite_branch_density * self.dendrite_count
        }

    def calculate_axon_volume(self) -> float:
        return math.pi * (self.axon_diameter / 2) ** 2 * self.axon_length

    def calculate_soma_volume(self) -> float:
        return (4/3) * math.pi * (self.soma_diameter / 2) ** 3

    def calculate_total_neuron_volume(self) -> float:
        soma_vol = self.calculate_soma_volume()
        axon_vol = self.calculate_axon_volume()
        dendrite_vol = self.dendrite_count * 10 * self.dendrite_branch_density
        
        return soma_vol + axon_vol + dendrite_vol

    def calculate_mitochondrial_distribution(self) -> Dict[str, float]:
        total_volume = self.calculate_total_neuron_volume()
        total_mitochondria = total_volume * self.mitochondria_density
        
        soma_mito = total_mitochondria * 0.4
        axon_mito = total_mitochondria * 0.3
        dendrite_mito = total_mitochondria * 0.3
        
        return {
            "soma": soma_mito,
            "axon": axon_mito,
            "dendrites": dendrite_mito,
            "total": total_mitochondria
        }

    def calculate_neurotransmitter_content(self) -> Dict[str, float]:
        content = {}
        for nt in self.neurotransmitter_types:
            molecules_per_vesicle = 5000
            total_molecules = (self.neurotransmitter_vesicles * 
                              molecules_per_vesicle)
            content[nt] = total_molecules
        
        return content

    def axonal_transport_rate(self, transport_type: str = "fast") -> float:
        if transport_type == "fast":
            base_rate = 400.0
        elif transport_type == "slow":
            base_rate = 1.0
        else:
            base_rate = 50.0
        
        health_factor = self.health / 100
        integrity_factor = self.structural_integrity / 100
        
        return base_rate * health_factor * integrity_factor

    def synaptic_vesicle_recycling_rate(self) -> float:
        base_rate = 0.1
        
        metabolic_factor = self.metabolism_rate
        health_factor = self.health / 100
        
        return base_rate * metabolic_factor * health_factor

    def dendritic_spine_turnover(self) -> Dict[str, float]:
        total_spines = self.synapse_count * 0.8
        
        formation_rate = total_spines * 0.05 * (self.health / 100)
        elimination_rate = total_spines * 0.03 * (1 - self.health / 100)
        
        net_change = formation_rate - elimination_rate
        
        return {
            "total_spines": total_spines,
            "formation_rate": formation_rate,
            "elimination_rate": elimination_rate,
            "net_change": net_change
        }

    def myelination_index(self) -> float:
        if self.myelin_thickness <= 0:
            return 0.0
        
        g_ratio = self.axon_diameter / (self.axon_diameter + 2 * self.myelin_thickness)
        
        optimal_g_ratio = 0.6
        myelination_quality = 1 - abs(g_ratio - optimal_g_ratio)
        
        return max(0, min(1, myelination_quality))

    def neuron_metabolic_rate(self) -> Dict[str, float]:
        base_metabolic_rate = self.calculate_total_neuron_volume() * 0.001
        
        synaptic_cost = self.synapse_count * 0.01
        ion_pump_cost = self.calculate_total_neuron_volume() * 0.005
        transport_cost = self.axon_length * 0.0001
        
        total_rate = (base_metabolic_rate + synaptic_cost + 
                     ion_pump_cost + transport_cost)
        
        atp_consumption = total_rate * 38
        
        return {
            "base_rate": base_metabolic_rate,
            "synaptic_cost": synaptic_cost,
            "ion_pump_cost": ion_pump_cost,
            "transport_cost": transport_cost,
            "total_metabolic_rate": total_rate,
            "atp_consumption": atp_consumption
        }

    def calcium_buffering_capacity(self) -> float:
        soma_volume = self.calculate_soma_volume()
        
        buffer_proteins = soma_volume * 100
        
        buffering_capacity = buffer_proteins * 0.001
        
        return buffering_capacity

    def neuron_structural_protein_content(self) -> Dict[str, float]:
        total_volume = self.calculate_total_neuron_volume()
        
        return {
            "neurofilaments": total_volume * self.neurofilament_density * 0.1,
            "microtubules": total_volume * 0.15,
            "actin": total_volume * 0.2,
            "tubulin": total_volume * 0.12,
            "MAP2": self.dendrite_count * 10,
            "tau": self.axon_length * 0.01
        }

    def assess_neurodegeneration_markers(self) -> Dict[str, float]:
        age_factor = min(1.0, self.age / 1000)
        
        tau_hyperphosphorylation = age_factor * (1 - self.health / 100) * 0.5
        
        amyloid_precursor = age_factor * self.mutation_count * 0.1
        
        synaptic_loss = max(0, 1 - self.synapse_count / 1000) * age_factor
        
        mitochondrial_dysfunction = (1 - self.structural_integrity / 100) * 0.3
        
        oxidative_stress = (self.age / 500) * (1 - self.health / 100)
        
        return {
            "tau_pathology": min(1.0, tau_hyperphosphorylation),
            "amyloid_burden": min(1.0, amyloid_precursor),
            "synaptic_loss": min(1.0, synaptic_loss),
            "mitochondrial_dysfunction": min(1.0, mitochondrial_dysfunction),
            "oxidative_stress": min(1.0, oxidative_stress),
            "overall_degeneration": min(1.0, (tau_hyperphosphorylation + 
                                             amyloid_precursor + 
                                             synaptic_loss + 
                                             mitochondrial_dysfunction + 
                                             oxidative_stress) / 5)
        }

    def neuron_repair_mechanisms(self) -> Dict[str, float]:
        dna_repair = self.repair_rate * 0.3
        
        protein_degradation = self.metabolism_rate * 0.2
        
        synaptic_plasticity = (self.health / 100) * 0.4
        
        neurotrophic_response = (self.structural_integrity / 100) * 0.3
        
        return {
            "dna_repair_capacity": dna_repair,
            "protein_quality_control": protein_degradation,
            "synaptic_plasticity": synaptic_plasticity,
            "neurotrophic_signaling": neurotrophic_response
        }

    def axon_initial_segment_properties(self) -> Dict[str, float]:
        sodium_channel_density = 50.0
        
        threshold_potential = -55.0 + (self.health / 100) * 5
        
        return {
            "length": self.axon_initial_segment_length,
            "sodium_channel_density": sodium_channel_density,
            "threshold_potential": threshold_potential,
            "excitability": sodium_channel_density * (self.health / 100)
        }

    def get_neuron_morphometry(self) -> Dict[str, any]:
        return {
            "soma_diameter": self.soma_diameter,
            "soma_volume": self.calculate_soma_volume(),
            "axon_length": self.axon_length,
            "axon_diameter": self.axon_diameter,
            "axon_volume": self.calculate_axon_volume(),
            "dendrite_count": self.dendrite_count,
            "dendrite_complexity": self.calculate_dendritic_arbor_complexity(),
            "total_volume": self.calculate_total_neuron_volume(),
            "surface_area": self.calculate_membrane_capacitance() / 1.0,
            "myelin_thickness": self.myelin_thickness,
            "myelination_index": self.myelination_index()
        }

    def get_electrophysiological_properties(self) -> Dict[str, float]:
        return {
            "resting_potential": self.resting_potential,
            "membrane_capacitance": self.calculate_membrane_capacitance(),
            "input_resistance": self.calculate_input_resistance(),
            "conduction_velocity": self.calculate_conduction_velocity(),
            "time_constant": (self.calculate_membrane_capacitance() * 
                            self.calculate_input_resistance())
        }

    def get_synaptic_properties(self) -> Dict[str, any]:
        return {
            "synapse_count": self.synapse_count,
            "synaptic_density": self.calculate_synaptic_density(),
            "neurotransmitter_types": self.neurotransmitter_types,
            "vesicle_count": self.neurotransmitter_vesicles,
            "neurotransmitter_content": self.calculate_neurotransmitter_content(),
            "spine_density": self.spine_density,
            "spine_morphology": self.dendritic_spine_morphology,
            "spine_turnover": self.dendritic_spine_turnover()
        }

    def neuron_aging_simulation(self, time_steps: int = 1) -> Dict[str, any]:
        for _ in range(time_steps):
            self.age += 1
            
            self.synapse_count = max(100, int(self.synapse_count * 0.999))
            self.spine_density = max(0.5, self.spine_density * 0.9995)
            
            self.dendrite_branch_density = max(0.3, 
                                              self.dendrite_branch_density * 0.9998)
            
            self.mitochondria_density = max(0.05, 
                                           self.mitochondria_density * 0.9997)
            
            self.health = max(0, self.health - 0.01)
            self.structural_integrity = max(0, self.structural_integrity - 0.02)
            
            if random.random() < 0.001:
                self.mutation_count += 1
        
        return {
            "age": self.age,
            "synapse_count": self.synapse_count,
            "spine_density": self.spine_density,
            "dendrite_complexity": self.dendrite_branch_density,
            "health": self.health,
            "degeneration_markers": self.assess_neurodegeneration_markers()
        }
