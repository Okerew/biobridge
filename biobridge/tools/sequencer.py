import random
from typing import List, Tuple


class DNASequencer:
    def __init__(self, error_rate: float = 0.001, read_length: int = 100):
        """
        Initialize a DNA Sequencer.

        :param error_rate: Probability of a sequencing error (default: 0.001)
        :param read_length: Length of each read (default: 100 nucleotides)
        """
        self.error_rate = error_rate
        self.read_length = read_length

    def sequence(self, dna: str) -> List[str]:
        """
        Sequence the given DNA, simulating the physical process with potential errors.

        :param dna: The DNA sequence to be sequenced
        :return: List of sequenced reads
        """
        reads = []
        for i in range(0, len(dna), self.read_length):
            read = dna[i:i + self.read_length]
            sequenced_read = self._introduce_errors(read)
            reads.append(sequenced_read)
        return reads

    def _introduce_errors(self, read: str) -> str:
        """
        Introduce sequencing errors into a read.

        :param read: The original read
        :return: The read with potential errors
        """
        nucleotides = 'ATCG'
        error_types = ['substitution', 'insertion', 'deletion']

        modified_read = list(read)
        i = 0
        while i < len(modified_read):
            if random.random() < self.error_rate:
                error_type = random.choice(error_types)
                if error_type == 'substitution':
                    modified_read[i] = random.choice(nucleotides.replace(modified_read[i], ''))
                elif error_type == 'insertion':
                    modified_read.insert(i, random.choice(nucleotides))
                    i += 1  # increment i to skip the newly inserted nucleotide
                elif error_type == 'deletion':
                    modified_read.pop(i)
            else:
                i += 1

        return ''.join(modified_read)

    def assemble(self, reads: List[str]) -> str:
        """
        Assemble the sequenced reads into a complete DNA sequence.
        This is a simplified assembly process and may not perfectly reconstruct the original sequence.

        :param reads: List of sequenced reads
        :return: Assembled DNA sequence
        """
        # Sort reads by length (longest first)
        sorted_reads = sorted(reads, key=len, reverse=True)

        # Start with the longest read
        assembled = sorted_reads[0]

        for read in sorted_reads[1:]:
            overlap = self._find_overlap(assembled, read)
            if overlap > 0:
                assembled += read[overlap:]
            else:
                assembled += read

        return assembled

    def _find_overlap(self, seq1: str, seq2: str) -> int:
        """
        Find the overlap between two sequences.

        :param seq1: First sequence
        :param seq2: Second sequence
        :return: Length of the overlap
        """
        max_overlap = min(len(seq1), len(seq2))
        for i in range(max_overlap, 0, -1):
            if seq1[-i:] == seq2[:i]:
                return i
        return 0

    def analyze_quality(self, original: str, sequenced: str) -> Tuple[float, float, float]:
        """
        Analyze the quality of the sequencing by comparing the original and sequenced DNA.

        :param original: The original DNA sequence
        :param sequenced: The sequenced DNA
        :return: Tuple of (accuracy, coverage, average_read_length)
        """
        # Calculate accuracy
        matches = sum(a == b for a, b in zip(original, sequenced))
        accuracy = matches / len(original) if len(original) > 0 else 0

        # Calculate coverage
        coverage = len(sequenced) / len(original) if len(original) > 0 else 0

        # Calculate average read length
        avg_read_length = sum(len(read) for read in self.sequence(original)) / len(self.sequence(original))

        return accuracy, coverage, avg_read_length
