from typing import List, Tuple, Optional
from biobridge.genes.dna import DNA
import random
import matplotlib.pyplot as plt


class ChromosomeArm:
    def __init__(self, dna: DNA, arm_type: str):
        self.dna = dna
        self.arm_type = arm_type  # 'p' for short arm, 'q' for long arm
        self.bands: List[Tuple[int, int, str]] = []  # (start, end, staining_pattern)

    def add_band(self, start: int, end: int, staining_pattern: str):
        self.bands.append((start, end, staining_pattern))

    def __len__(self):
        return len(self.dna)


class Chromosome:
    def __init__(self, dna: DNA, name: str):
        self.name = name
        self.p_arm: Optional[ChromosomeArm] = None
        self.q_arm: Optional[ChromosomeArm] = None
        self.centromere_position = len(dna) // 2  # Default centromere position
        self.telomere_length = 100  # Default telomere length
        self.set_arms(dna)
        self.chromosome_type = "Metacentric"  # Default type
        self.satellite_dna: Optional[DNA] = None
        self.constrictions: List[int] = []  # Positions of constrictions

    def set_arms(self, dna: DNA):
        """Split the DNA into p and q arms based on centromere position."""
        p_sequence = dna.get_sequence(1)[:self.centromere_position]
        q_sequence = dna.get_sequence(1)[self.centromere_position:]
        self.p_arm = ChromosomeArm(DNA(p_sequence), 'p')
        self.q_arm = ChromosomeArm(DNA(q_sequence), 'q')

    def set_chromosome_type(self, chr_type: str):
        """Set the chromosome type (Metacentric, Submetacentric, Acrocentric, Telocentric)."""
        valid_types = ["Metacentric", "Submetacentric", "Acrocentric", "Telocentric"]
        if chr_type in valid_types:
            self.chromosome_type = chr_type
        else:
            raise ValueError(f"Invalid chromosome type. Must be one of {valid_types}")

    def add_satellite_dna(self, satellite: DNA):
        """Add satellite DNA to the chromosome."""
        self.satellite_dna = satellite

    def add_constriction(self, position: int):
        """Add a constriction to the chromosome."""
        if 0 <= position < len(self):
            self.constrictions.append(position)
        else:
            raise ValueError("Constriction position must be within the chromosome length.")

    def add_band(self, arm: str, start: int, end: int, staining_pattern: str):
        """Add a band to either the p or q arm."""
        if arm == 'p':
            self.p_arm.add_band(start, end, staining_pattern)
        elif arm == 'q':
            self.q_arm.add_band(start, end, staining_pattern)
        else:
            raise ValueError("Arm must be either 'p' or 'q'")

    def replicate(self, mutation_rate: float = 0.001):
        """Replicate the chromosome, potentially introducing mutations."""
        new_p_dna = self.p_arm.dna.replicate(mutation_rate)
        new_q_dna = self.q_arm.dna.replicate(mutation_rate)
        new_dna = DNA(new_p_dna.get_sequence(1) + new_q_dna.get_sequence(1))
        new_chromosome = Chromosome(new_dna, f"{self.name}_copy")
        new_chromosome.centromere_position = self.centromere_position
        new_chromosome.telomere_length = self.telomere_length
        new_chromosome.chromosome_type = self.chromosome_type
        if self.satellite_dna:
            new_chromosome.satellite_dna = self.satellite_dna.replicate(mutation_rate)
        new_chromosome.constrictions = self.constrictions.copy()
        return new_chromosome

    def crossover(self, other: 'Chromosome', crossover_points: List[int]):
        """Perform crossover with another chromosome."""
        if len(self) != len(other):
            raise ValueError("Chromosomes must be of equal length for crossover.")

        new_sequence = ""
        current_chromosome = self
        max_length = min(len(self), len(other))  # Use the shorter length

        for i in range(max_length):
            if i in crossover_points:
                current_chromosome = other if current_chromosome == self else self
            new_sequence += str(current_chromosome[i])

        # If one chromosome is longer, append the remaining part
        if len(self) > max_length:
            new_sequence += str(self[max_length:])
        elif len(other) > max_length:
            new_sequence += str(other[max_length:])

        new_dna = DNA(new_sequence)
        new_chromosome = Chromosome(new_dna, f"{self.name}_crossover")
        new_chromosome.centromere_position = self.centromere_position
        new_chromosome.telomere_length = self.telomere_length
        new_chromosome.chromosome_type = self.chromosome_type
        return new_chromosome

    def mutate(self, mutation_rate: float = 0.001):
        """Introduce random mutations in the chromosome."""
        self.p_arm.dna = DNA(self._mutate_sequence(self.p_arm.dna.get_sequence(1), mutation_rate))
        self.q_arm.dna = DNA(self._mutate_sequence(self.q_arm.dna.get_sequence(1), mutation_rate))

    def _mutate_sequence(self, sequence: str, mutation_rate: float) -> str:
        return ''.join(random.choice(['A', 'T', 'C', 'G']) if random.random() < mutation_rate else base
                       for base in sequence)

    def invert(self, start: int, end: int):
        """Invert a segment of the chromosome."""
        p_len = len(self.p_arm)
        if start < p_len and end <= p_len:
            self.p_arm.dna = self._invert_dna_segment(self.p_arm.dna, start, end)
        elif start >= p_len and end > p_len:
            self.q_arm.dna = self._invert_dna_segment(self.q_arm.dna, start - p_len, end - p_len)
        else:
            # Inversion spans both arms
            p_segment = self.p_arm.dna.get_sequence(1)[start:] if start < p_len else ""
            q_segment = self.q_arm.dna.get_sequence(1)[:end - p_len] if end > p_len else ""
            inverted_segment = (p_segment + q_segment)[::-1]
            self.p_arm.dna = DNA(self.p_arm.dna.get_sequence(1)[:start] + inverted_segment[:p_len - start])
            self.q_arm.dna = DNA(inverted_segment[p_len - start:] + self.q_arm.dna.get_sequence(1)[end - p_len:])

    def _invert_dna_segment(self, dna: DNA, start: int, end: int) -> DNA:
        sequence = dna.get_sequence(1)
        inverted_segment = sequence[start:end][::-1]
        new_sequence = sequence[:start] + inverted_segment + sequence[end:]
        return DNA(new_sequence)

    def transpose(self, start: int, end: int, new_position: int):
        """Transpose a segment of the chromosome to a new position."""
        full_sequence = self.get_sequence()
        segment = full_sequence[start:end]
        new_sequence = (
                full_sequence[:start] +
                full_sequence[end:new_position] +
                segment +
                full_sequence[new_position:]
        )
        self.set_arms(DNA(new_sequence))

    def get_sequence(self) -> str:
        """Get the full DNA sequence of the chromosome."""
        return self.p_arm.dna.get_sequence(1) + self.q_arm.dna.get_sequence(1)

    def set_centromere(self, position: int):
        """Set the position of the centromere and update arms."""
        if 0 <= position < len(self):
            self.centromere_position = position
            self.set_arms(DNA(self.get_sequence()))
        else:
            raise ValueError("Centromere position must be within the chromosome length.")

    def set_telomere_length(self, length: int):
        """Set the length of the telomeres."""
        if length > 0:
            self.telomere_length = length
        else:
            raise ValueError("Telomere length must be positive.")

    def get_gc_content(self) -> float:
        """Calculate the GC content of the chromosome."""
        return (self.p_arm.dna.gc_content() * len(self.p_arm) +
                self.q_arm.dna.gc_content() * len(self.q_arm)) / len(self)

    def find_genes(self, min_length: int = 100) -> List[Tuple[int, int, str]]:
        """Find potential genes in the chromosome."""
        p_genes = self.p_arm.dna.find_orfs(min_length)
        q_genes = [(start + len(self.p_arm), end + len(self.p_arm), seq)
                   for start, end, seq in self.q_arm.dna.find_orfs(min_length)]
        return p_genes + q_genes

    def visualize(self):
        """Visualize the chromosome structure, including arms, bands, and other features."""
        fig, ax = plt.subplots(figsize=(12, 4))

        # Plot GC content
        gc_content = [1 if base in ['G', 'C'] else 0 for base in self.get_sequence()]
        ax.plot(gc_content, color='blue', alpha=0.5, label='GC Content')

        # Plot chromosome structure
        ax.axvline(x=self.centromere_position, color='red', linestyle='--', label='Centromere')
        ax.axvline(x=self.telomere_length, color='green', linestyle=':', label='Telomere')
        ax.axvline(x=len(self) - self.telomere_length, color='green', linestyle=':', label='Telomere')

        # Plot constrictions
        for constriction in self.constrictions:
            ax.axvline(x=constriction, color='purple', linestyle='-.', label='Constriction')

        # Plot bands
        for arm in [self.p_arm, self.q_arm]:
            offset = 0 if arm.arm_type == 'p' else len(self.p_arm)
            for start, end, pattern in arm.bands:
                ax.axvspan(start + offset, end + offset, facecolor='gray', alpha=0.3)

        # Plot satellite DNA if present
        if self.satellite_dna:
            ax.axvspan(len(self) - len(self.satellite_dna), len(self), facecolor='yellow', alpha=0.3,
                       label='Satellite DNA')

        ax.set_title(f"Chromosome {self.name} Structure ({self.chromosome_type})")
        ax.set_xlabel("Position")
        ax.set_ylabel("Features")
        ax.legend()
        plt.show()

    def compare(self, other: 'Chromosome') -> float:
        """Compare this chromosome with another and return similarity score."""
        if len(self) != len(other):
            raise ValueError("Chromosomes must be of equal length for comparison.")

        sequence1 = self.get_sequence()
        sequence2 = other.get_sequence()
        matches = sum(b1 == b2 for b1, b2 in zip(sequence1, sequence2))
        return matches / len(sequence1)

    def to_dict(self) -> dict:
        """Convert the chromosome to a dictionary representation."""
        return {
            'name': self.name,
            'p_arm': self.p_arm.dna.to_dict(),
            'q_arm': self.q_arm.dna.to_dict(),
            'centromere_position': self.centromere_position,
            'telomere_length': self.telomere_length,
            'chromosome_type': self.chromosome_type,
            'satellite_dna': self.satellite_dna.to_dict() if self.satellite_dna else None,
            'constrictions': self.constrictions,
            'p_arm_bands': self.p_arm.bands,
            'q_arm_bands': self.q_arm.bands
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Chromosome':
        """Create a chromosome from a dictionary representation."""
        chromosome = cls(DNA(data['p_arm']['sequence'] + data['q_arm']['sequence']), data['name'])
        chromosome.centromere_position = data['centromere_position']
        chromosome.telomere_length = data['telomere_length']
        chromosome.chromosome_type = data['chromosome_type']
        if data['satellite_dna']:
            chromosome.satellite_dna = DNA.from_dict(data['satellite_dna'])
        chromosome.constrictions = data['constrictions']
        chromosome.p_arm.bands = data['p_arm_bands']
        chromosome.q_arm.bands = data['q_arm_bands']
        return chromosome

    def __str__(self):
        return f"Chromosome {self.name} ({self.chromosome_type}): {self.get_sequence()[:50]}..."

    def __len__(self):
        return len(self.p_arm) + len(self.q_arm)

    def __eq__(self, other):
        if isinstance(other, Chromosome):
            return (self.get_sequence() == other.get_sequence() and
                    self.name == other.name and
                    self.chromosome_type == other.chromosome_type)
        return False

    def __hash__(self):
        return hash((self.name, self.get_sequence(), self.chromosome_type))

    def __getitem__(self, index):
        """Allow indexing of the chromosome with wrap-around behavior."""
        full_sequence = self.get_sequence()
        if not full_sequence:
            raise ValueError("The chromosome sequence is empty.")

        if isinstance(index, int):
            return full_sequence[index % len(full_sequence)]
        elif isinstance(index, slice):
            start, stop, step = index.indices(len(full_sequence))
            return full_sequence[start % len(full_sequence):stop % len(full_sequence):step]
        else:
            raise TypeError(f"Chromosome indices must be integers or slices, not {type(index).__name__}")
