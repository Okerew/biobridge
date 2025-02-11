import random
import re


class PCR:
    def __init__(self, sequence, forward_primer, reverse_primer, cycles=30, mutation_rate=0.001):
        """
        Initialize a new PCR object.

        :param sequence: The nucleotide sequence of the DNA or RNA strand
        :param forward_primer: The forward primer sequence
        :param reverse_primer: The reverse primer sequence
        :param cycles: Number of PCR cycles (default is 30)
        :param mutation_rate: The probability of a mutation occurring at each nucleotide (default is 0.001)
        """
        self.sequence = sequence.upper()
        self.forward_primer = forward_primer.upper()
        self.reverse_primer = reverse_primer.upper()
        self.cycles = cycles
        self.mutation_rate = mutation_rate

    def find_primer_binding_sites(self):
        """
        Find the binding sites of the forward and reverse primers in the sequence.

        :return: Tuple of start positions of forward and reverse primers
        """
        forward_positions = [m.start() for m in re.finditer(self.forward_primer, self.sequence)]
        reverse_positions = [m.start() for m in re.finditer(self.reverse_primer, self.sequence)]
        return forward_positions, reverse_positions

    def amplify(self):
        """
        Simulate the PCR amplification process.

        :return: List of amplified sequences
        """
        forward_positions, reverse_positions = self.find_primer_binding_sites()
        amplified_sequences = []

        for _ in range(self.cycles):
            for forward_pos in forward_positions:
                for reverse_pos in reverse_positions:
                    if forward_pos < reverse_pos:
                        amplified_sequence = self.sequence[forward_pos:reverse_pos + len(self.reverse_primer)]
                        amplified_sequence = self.introduce_mutations(amplified_sequence)
                        amplified_sequences.append(amplified_sequence)

        return amplified_sequences

    def introduce_mutations(self, sequence):
        """
        Introduce random mutations into the sequence.

        :param sequence: The nucleotide sequence to mutate
        :return: The mutated sequence
        """
        new_sequence = ""
        for nucleotide in sequence:
            if random.random() < self.mutation_rate:
                new_nucleotide = random.choice(['A', 'T', 'C', 'G'])
                new_sequence += new_nucleotide
            else:
                new_sequence += nucleotide
        return new_sequence

    def describe(self):
        """
        Provide a detailed description of the PCR process.
        """
        description = f"PCR Process:\n"
        description += f"Sequence: {self.sequence}\n"
        description += f"Forward Primer: {self.forward_primer}\n"
        description += f"Reverse Primer: {self.reverse_primer}\n"
        description += f"Cycles: {self.cycles}\n"
        description += f"Mutation Rate: {self.mutation_rate}\n"
        return description

    def __str__(self):
        """
        Return a string representation of the PCR process.
        """
        return self.describe()