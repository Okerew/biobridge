import random
from typing import List, Dict
from enum import Enum, auto
from biobridge.blocks.cell import Cell
from biobridge.genes.dna import DNA
from biobridge.networks.system import System

class MutationType(Enum):
    POINT_MUTATION = auto()
    FRAME_SHIFT = auto()
    DELETION = auto()
    INSERTION = auto()

class EnvironmentalFactor:
    def __init__(self, name: str, intensity: float, impact_type: str):
        self.name = name
        self.intensity = intensity
        self.impact_type = impact_type  # 'stress', 'repair', 'mutation'

class SelfRepairingCell(Cell):
    """
    Enhanced cell class with advanced self-repair and mutation control mechanisms
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dna_repair_efficiency = kwargs.get('dna_repair_efficiency', 0.95)
        self.rejuvenation_threshold = kwargs.get('rejuvenation_threshold', 50)
        self.max_mutation_tolerance = kwargs.get('max_mutation_tolerance', 10)
        
        # New attributes from improved version
        self.cell_cycle_stage = 'G1'
        self.stress_level = 0.0
        
    def enhanced_divide(self):
        """
        Advanced division with telomere and epigenetic controls
        """
        # Telomere-aware division
        if random.random() > self.telomere_protection_level:
            print(f"Cell {self.name} division prevented due to telomere protection.")
            return None
        
        # Conditional epigenetic reset
        if self.age > self.epigenetic_reset_threshold:
            self._partial_reprogramming()
        
        # Original division logic with enhanced checks
        daughter_cell = super().divide() if random.random() < 0.8 else None
        
        return daughter_cell
    
    def _partial_reprogramming(self):
        """
        Controlled gene expression reset inspired by Yamanaka factors
        """
        reset_genes = ['OCT4', 'SOX2', 'KLF4', 'MYC']
        
        if self.dna:
            for gene in reset_genes:
                if random.random() < 0.4:  # More controlled activation
                    self.dna.add_gene(gene, "SIMULATEDSEQUENCE", "controlled")
        
        # Moderate health and age restoration
        self.health = min(100, self.health + 15)
        self.age = max(0, self.age - 3)
    
    def metabolic_pathway_switch(self):
        """
        Enhanced metabolic pathway selection with redundancy
        """
        current_pathway = random.choices(
            list(self.metabolic_pathways.keys()), 
            weights=list(self.metabolic_pathways.values())
        )[0]
        
        # More sophisticated metabolic adaptation
        pathway_effects = {
            'glycolysis': {'metabolism': 1.2, 'repair': 1.0},
            'fatty_acid_oxidation': {'metabolism': 1.1, 'repair': 1.1},
            'glutaminolysis': {'metabolism': 1.0, 'repair': 1.2},
            'mitochondrial_backup': {'metabolism': 0.9, 'repair': 1.3}
        }
        
        effects = pathway_effects.get(current_pathway, {})
        self.metabolism_rate *= effects.get('metabolism', 1.0)
        self.repair_rate *= effects.get('repair', 1.0)

    def _pass_cell_cycle_checkpoints(self) -> bool:
        """Simulate cell cycle checkpoint validation"""
        checkpoint_map = {
            'G1': random.random() < 0.8,
            'G2': random.random() < 0.9,
            'metaphase': random.random() < 0.95
        }
        return checkpoint_map.get(self.cell_cycle_stage, False)
    
    def _is_apoptosis_required(self) -> bool:
        """Determine if cell should undergo programmed cell death"""
        return (
            self.mutation_count > self.max_mutation_tolerance * 1.5 or 
            self.health < 10
        )
    
    def trigger_apoptosis(self):
        """Simulate programmed cell death"""
        print(f"Cell {self.name} triggered apoptosis due to critical damage")
    
    
class SelfRepairingDNA(DNA):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repair_enzymes = ['TP53', 'BRCA1', 'BRCA2', 'PARP1']
        self.mutation_limit = 20
        
        # Detailed mutation type mapping
        self.mutation_map = {
            MutationType.POINT_MUTATION: {
                'repair_probability': 0.7,
                'detection_threshold': 0.8,
                'repair_mechanism': self._point_mutation_repair
            },
            MutationType.FRAME_SHIFT: {
                'repair_probability': 0.4,
                'detection_threshold': 0.6,
                'repair_mechanism': self._frame_shift_repair
            },
            MutationType.DELETION: {
                'repair_probability': 0.3,
                'detection_threshold': 0.5,
                'repair_mechanism': self._deletion_repair
            },
            MutationType.INSERTION: {
                'repair_probability': 0.2,
                'detection_threshold': 0.4,
                'repair_mechanism': self._insertion_repair
            }
        }
        
        # Advanced error detection parameters
        self.error_sensing_threshold = 0.05
        self.repair_checkpoint_sensitivity = 0.9
        
        # Mutation tracking
        self.mutation_history = []
    
    def advanced_mutation_repair(self):
        """
        Comprehensive mutation repair with multi-stage error detection and correction
        """
        # Preliminary error sensing
        if random.random() < self.error_sensing_threshold:
            for mutation_type, mutation_data in self.mutation_map.items():
                # Probabilistic mutation type detection
                if random.random() < mutation_data['detection_threshold']:
                    # Checkpoint-sensitive repair mechanism
                    repair_chance = (
                        mutation_data['repair_probability'] * 
                        self.repair_checkpoint_sensitivity
                    )
                    
                    if random.random() < repair_chance:
                        # Execute type-specific repair mechanism
                        mutation_data['repair_mechanism']()
                        
                        # Log repair event
                        self.mutation_history.append({
                            'type': mutation_type,
                            'timestamp': random.random(),
                            'repaired': True
                        })
        
        # Comprehensive repair for accumulated mutations
        self._check_comprehensive_repair()
    
    def _check_comprehensive_repair(self):
        """
        Trigger comprehensive repair based on mutation accumulation
        """
        # Advanced mutation counting with weighted approach
        mutation_weights = {
            MutationType.POINT_MUTATION: 1,
            MutationType.FRAME_SHIFT: 3,
            MutationType.DELETION: 2,
            MutationType.INSERTION: 2
        }
        
        weighted_mutation_count = sum(
            mutation_weights.get(entry['type'], 1) 
            for entry in self.mutation_history 
            if not entry.get('repaired', False)
        )
        
        if weighted_mutation_count > self.mutation_limit:
            self.comprehensive_repair()
    
    def _point_mutation_repair(self):
        """
        Advanced point mutation repair mechanism
        """
        # Simulate base pair correction
        sequence = list(self.get_sequence(1))
        for i in range(len(sequence)):
            # Random base correction with probability
            if random.random() < 0.2:
                sequence[i] = random.choice(['A', 'T', 'C', 'G'])
        
        corrected_sequence = ''.join(sequence)
        self.__init__(corrected_sequence)
        print("Point mutation repair performed.")
    
    def _frame_shift_repair(self):
        """
        Sophisticated frame shift mutation repair
        """
        sequence = self.get_sequence(1)
        
        # Detect and correct frame shift
        correction_strategies = [
            # Insertion compensation
            lambda seq: seq + random.choice(['A', 'T', 'C', 'G']),
            # Deletion compensation
            lambda seq: seq[:-1],
            # Substitution-based correction
            lambda seq: seq[:-1] + random.choice(['A', 'T', 'C', 'G'])
        ]
        
        corrected_sequence = random.choice(correction_strategies)(sequence)
        self.__init__(corrected_sequence)
        print("Frame shift mutation repaired.")
    
    def _deletion_repair(self):
        """
        Comprehensive deletion mutation repair
        """
        sequence = self.get_sequence(1)
        
        # Reconstruction strategies
        if len(sequence) > 10:
            # Partial sequence reconstruction
            reconstruction_point = random.randint(3, len(sequence) - 3)
            corrected_sequence = (
                sequence[:reconstruction_point] + 
                ''.join(random.choice(['A', 'T', 'C', 'G']) for _ in range(3)) + 
                sequence[reconstruction_point:]
            )
        else:
            # Complete sequence regeneration
            corrected_sequence = ''.join(
                random.choice(['A', 'T', 'C', 'G']) for _ in range(len(sequence))
            )
        
        self.__init__(corrected_sequence)
        print("Deletion mutation repaired.")
    
    def _insertion_repair(self):
        """
        Precise insertion mutation repair
        """
        sequence = self.get_sequence(1)
        
        # Multiple repair strategies
        repair_strategies = [
            # Remove excess insertions
            lambda seq: seq[:len(seq)//2] + seq[len(seq)//2 + 3:],
            # Trim redundant sequences
            lambda seq: seq[:len(seq) - 3],
            # Selective sequence truncation
            lambda seq: seq[3:]
        ]
        
        corrected_sequence = random.choice(repair_strategies)(sequence)
        self.__init__(corrected_sequence)
        print("Insertion mutation repaired.")
    
    def comprehensive_repair(self):
        """
        Ultimate DNA repair mechanism
        """
        # Advanced repair enzyme activation
        repair_probability = len(self.repair_enzymes) * 0.15
        
        if random.random() < repair_probability:
            # Intelligent sequence reconstruction
            base_diversity = ['A', 'T', 'C', 'G']
            reconstruction_strategies = [
                # Partial preservation
                lambda seq: ''.join(
                    base if random.random() > 0.1 else random.choice(base_diversity) 
                    for base in seq
                ),
                # Complete regeneration with preservation probability
                lambda seq: ''.join(
                    random.choice(base_diversity) if random.random() > 0.3 else base 
                    for base in seq
                )
            ]
            
            current_sequence = self.get_sequence(1)
            corrected_sequence = random.choice(reconstruction_strategies)(current_sequence)
            
            # Reset mutation history
            self.mutation_history = []
            
            # Reinitialize with corrected sequence
            self.__init__(corrected_sequence)
            print("Advanced comprehensive DNA repair completed.")
    
class SelfRepairingHuman(System):
    def __init__(self, name: str = "Human System", initial_cells: int = 10):
        super().__init__(name)
        
        self.stem_cells: List[SelfRepairingCell] = []
        self.immune_system_efficiency = 0.95
        self.beneficial_mutation_chance = 0.1
        
        self._initialize_cells(initial_cells)
    
    def _initialize_cells(self, count):
        """Initialize the initial cell population"""
        for i in range(count):
            dna = SelfRepairingDNA(''.join(random.choice(['A','T','C','G']) for _ in range(100)))
            cell = SelfRepairingCell(
                name=f"Cell_{i}", 
                dna=dna,
                cell_type=random.choice(['neuron', 'muscle', 'epithelial'])
            )
            self.add_cell(cell)
    
    def create_stem_cell(self):
        """Create a programmable stem cell"""
        dna = SelfRepairingDNA(''.join(random.choice(['A','T','C','G']) for _ in range(100)))
        stem_cell = SelfRepairingCell(
            name=f"StemCell_{len(self.stem_cells)}",
            dna=dna,
            cell_type='stem'
        )
        self.stem_cells.append(stem_cell)
        self.add_cell(stem_cell)
        return stem_cell
    
    def simulate_time_step(self, external_factors: List[EnvironmentalFactor]):
        """
        More sophisticated time step with comprehensive system management
        """
        # Process environmental interactions
        for factor in external_factors:
            self._process_environmental_factor(factor)
        
        # Enhanced system-level operations
        super().simulate_time_step(
            [(factor.name, factor.intensity) for factor in external_factors]
        )
        
        # Advanced cellular maintenance
        self.intelligent_immune_scan()
        self.strategic_tissue_regeneration()
        self.adaptive_mutation_control()
    
    def intelligent_immune_scan(self):
        """
        Enhanced immune surveillance with selective cellular pruning
        """
        # More sophisticated damage assessment
        damaged_cells = [
            cell for cell in self.individual_cells 
            if cell.mutation_count > 7 or cell.health < 25 or cell.age > 50
        ]
        
        for cell in damaged_cells:
            if random.random() < self.senescence_elimination_rate:
                self.remove_cell(cell)
                print(f"Selectively removed aging cell: {cell.name}")
    
    def strategic_tissue_regeneration(self):
        """
        Targeted stem cell deployment for tissue maintenance
        """
        if len(self.individual_cells) < 10:
            # More intelligent stem cell generation
            for _ in range(random.randint(2, 5)):
                self.create_stem_cell()
    
    def adaptive_mutation_control(self):
        """
        Dynamic mutation regulation with AI-inspired approach
        """
        for cell in self.individual_cells:
            if hasattr(cell, 'dna'):
                # Probabilistic advanced mutation repair
                if random.random() < 0.3:
                    cell.dna.advanced_mutation_repair()

    
    def _process_environmental_factor(self, factor: EnvironmentalFactor):
        """
        Process and apply environmental factor effects
        """
        impact_handlers = {
            'stress': self._handle_stress_impact,
            'repair': self._handle_repair_impact,
            'mutation': self._handle_mutation_impact
        }
        
        handler = impact_handlers.get(factor.impact_type)
        if handler:
            handler(factor)
    
    def _handle_stress_impact(self, factor: EnvironmentalFactor):
        """Adjust system stress based on environmental factor"""
        for cell in self.individual_cells:
            cell.stress_level += factor.intensity * 0.1
    
    def _handle_repair_impact(self, factor: EnvironmentalFactor):
        """Enhance repair mechanisms"""
        self.immune_system_efficiency *= (1 + factor.intensity * 0.2)
    
    def _handle_mutation_impact(self, factor: EnvironmentalFactor):
        """Modulate mutation rates"""
        self.beneficial_mutation_chance *= (1 - factor.intensity * 0.1)
    
    def regenerate_tissues(self):
        """Use stem cells to replace lost or damaged cells"""
        if len(self.individual_cells) < 5:
            for _ in range(3):
                self.create_stem_cell()
    
    def regulate_mutations(self):
        """Control and regulate cellular mutations"""
        for cell in self.individual_cells:
            if random.random() < self.beneficial_mutation_chance:
                if hasattr(cell, 'dna'):
                    cell.dna.advanced_mutation_repair()


# Example usage
human_system = SelfRepairingHuman(initial_cells=20)
environmental_factors = [
    EnvironmentalFactor("Radiation", 0.3, "mutation"),
    EnvironmentalFactor("Growth Hormone", 0.6, "repair"),
    EnvironmentalFactor("Oxidative Stress", 0.4, "stress")
]

for _ in range(20):
    human_system.simulate_time_step(environmental_factors)
    print(human_system.get_system_status())