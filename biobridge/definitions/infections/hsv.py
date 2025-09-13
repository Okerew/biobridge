import random
from typing import List, Optional, Dict, Tuple
from enum import Enum
from biobridge.genes.dna import DNA, Nucleotide
from biobridge.enviromental.infection import Infection, InfectionType, Cell

class HSVState(Enum):
    LATENT = "latent"
    LYTIC = "lytic"
    DORMANT = "dormant"

class HSV(DNA, Infection):
    def __init__(self, 
                 sequence: str, 
                 name: str = "HSV-1",
                 spread_rate: float = 0.7,
                 latency_probability: float = 0.3,
                 reactivation_probability: float = 0.2):
        """
        Initialize a new HSV virus instance.
        
        :param sequence: The nucleotide sequence of the viral DNA
        :param name: Name of the virus strain
        :param spread_rate: Rate of viral spread (0.0 to 1.0)
        :param latency_probability: Probability of entering latent state
        :param reactivation_probability: Probability of reactivating from latency
        """
        # Initialize both parent classes
        DNA.__init__(self, sequence)
        Infection.__init__(self, name, InfectionType.VIRUS, spread_rate, sequence)
        
        # HSV-specific attributes
        self.state = HSVState.LYTIC
        self.latency_probability = latency_probability
        self.reactivation_probability = reactivation_probability
        self.host_dna: Optional[DNA] = None
        self.integration_sites: List[Tuple[int, int]] = []
        self.viral_proteins: Dict[str, str] = {
            "ICP0": "",  # Immediate-early protein 0
            "ICP4": "",  # Immediate-early protein 4
            "VP16": "",  # Virion protein 16
            "gB": "",    # Glycoprotein B
            "gD": ""     # Glycoprotein D
        }
        self.mutation_rate = 0.01  # Add mutation rate for DNA mutations

    def replicate(self, cell: 'Cell') -> None:
        """
        Override parent's replicate method to handle both viral replication and cell damage.
        
        :param cell: The infected cell
        """
        if cell.name in self.infected_cells:
            # Decrease cell health
            damage = random.uniform(5, 15)
            cell.health = max(0, cell.health - damage)
            
            # Chance to mutate during replication
            if random.random() < self.mutation_rate:
                self.viral_mutate()

    def viral_mutate(self) -> None:
        """
        HSV-specific mutation method that handles both DNA and viral characteristics.
        This replaces the parent classes' mutate methods to avoid conflicts.
        """
        # Mutate DNA sequence
        sequence = self.get_sequence(1)
        mutation_point = random.randint(0, len(sequence) - 1)
        new_base = random.choice(['A', 'T', 'C', 'G'])
        new_sequence = (
            sequence[:mutation_point] +
            new_base +
            sequence[mutation_point + 1:]
        )
        self.strand1 = [Nucleotide(base) for base in new_sequence]
        self.strand2 = [nucleotide.complement() for nucleotide in self.strand1]
        
        # Mutate viral characteristics
        if random.random() < 0.1:  # 10% chance to modify spread rate
            self.spread_rate *= random.uniform(0.8, 1.2)
            self.spread_rate = max(0.0, min(1.0, self.spread_rate))
        
        if random.random() < 0.1:  # 10% chance to modify latency/reactivation probabilities
            self.latency_probability *= random.uniform(0.8, 1.2)
            self.reactivation_probability *= random.uniform(0.8, 1.2)
            
            # Ensure probabilities stay between 0 and 1
            self.latency_probability = max(0.0, min(1.0, self.latency_probability))
            self.reactivation_probability = max(0.0, min(1.0, self.reactivation_probability))

    def integrate_into_host(self, host_dna: DNA, position: int) -> bool:
        """
        Integrate viral DNA into host genome.
    
        :param host_dna: Host cell's DNA
        :param position: Integration position in host genome
        :return: Success of integration
        """
        # Remove the state check since integration should be possible in any state
        try:
            self.host_dna = host_dna
            viral_sequence = self.get_sequence(1)
        
            # Ensure position is within valid range
            if position < 0 or position > len(host_dna.get_sequence(1)):
                print("Invalid integration position")
                return False
            
            integration_end = position + len(viral_sequence)
        
            # Store integration site
            self.integration_sites.append((position, integration_end))
        
            # Update host DNA sequence
            host_sequence = host_dna.get_sequence(1)
            new_sequence = (
                host_sequence[:position] +
                viral_sequence +
                host_sequence[position:]
            )
        
            host_dna.strand1 = [Nucleotide(base) for base in new_sequence]
            host_dna.strand2 = [nucleotide.complement() for nucleotide in host_dna.strand1]
        
            print(f"Successfully integrated viral DNA at position {position}")
            return True
        
        except Exception as e:
            print(f"Integration failed: {str(e)}")
            return False


    def enter_latency(self, cell: 'Cell') -> bool:
        """
        Attempt to enter latent state in a neuron.
        
        :param cell: Target cell
        :return: Success of entering latency
        """
        if random.random() < self.latency_probability and cell.cell_type == "neuron":
            self.state = HSVState.LATENT
            return True
        return False

    def reactivate(self) -> bool:
        """
        Attempt to reactivate from latency.
        
        :return: Success of reactivation
        """
        if self.state == HSVState.LATENT and random.random() < self.reactivation_probability:
            self.state = HSVState.LYTIC
            # Extract viral DNA from host if integrated
            if self.host_dna and self.integration_sites:
                self._extract_from_host()
            return True
        return False

    def _extract_from_host(self) -> None:
        """Extract viral DNA from host genome during reactivation."""
        if self.host_dna and self.integration_sites:
            for start, end in reversed(self.integration_sites):
                host_sequence = self.host_dna.get_sequence(1)
                new_sequence = host_sequence[:start] + host_sequence[end:]
                self.host_dna.strand1 = [Nucleotide(base) for base in new_sequence]
                self.host_dna.strand2 = [nucleotide.complement() for nucleotide in self.host_dna.strand1]
            self.integration_sites.clear()

    def express_viral_proteins(self) -> Dict[str, bool]:
        """
        Express viral proteins based on the current state.
        
        :return: Dictionary of protein expression success
        """
        expression_results = {}
        
        if self.state == HSVState.LYTIC:
            # Express all proteins in lytic phase
            for protein in self.viral_proteins:
                expression_results[protein] = True
        elif self.state == HSVState.LATENT:
            # Express only latency-associated proteins
            for protein in self.viral_proteins:
                expression_results[protein] = protein in ["LAT"]  # Latency Associated Transcript
        
        return expression_results

    def infect(self, cell: 'Cell') -> bool:
        """
        Override parent's infect method to include HSV-specific behavior.
        
        :param cell: Target cell
        :return: Success of infection
        """
        if super().infect(cell):
            # HSV-specific infection logic
            if cell.cell_type == "neuron":
                self.enter_latency(cell)
            return True
        return False

    def mutate(self) -> None:
        """
        Public interface for mutation - calls the viral_mutate method.
        This maintains compatibility with the parent class method signatures.
        """
        self.viral_mutate()

    def describe(self) -> str:
        """
        Override parent's describe method to include HSV-specific information.
        """
        dna_description = DNA.describe(self)
        infection_description = Infection.describe(self)
        
        hsv_specific = f"""
HSV State: {self.state.value}
Latency Probability: {self.latency_probability:.2f}
Reactivation Probability: {self.reactivation_probability:.2f}
Integration Sites: {len(self.integration_sites)}
Active Viral Proteins: {[p for p, active in self.express_viral_proteins().items() if active]}
        """.strip()
        
        return f"{dna_description}\n{infection_description}\n{hsv_specific}"