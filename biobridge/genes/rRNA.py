import random
import json
from biobridge.genes.mRNA import mRNA


class rRNA:
    def __init__(self, sequence, id):
        """
        Initialize a new rRNA object.
        rRNA is typically a long precursor that undergoes processing to become functional.

        :param sequence: The nucleotide sequence of the rRNA strand (pre-rRNA)
        """
        self.sequence = sequence.upper().replace('T', 'U')
        self.mutation_probabilities = {
            'A': 0.1, 'C': 0.2, 'G': 0.3, 'U': 0.4
        }
        self.processed_rRNA = None
        self.cleavage_sites = ['ACG', 'GUU']
        self.id = id

    def mutate(self, index, new_nucleotide):
        """
        Mutate the rRNA sequence at a specific index.

        :param index: The position in the sequence to mutate
        :param new_nucleotide: The new nucleotide (A, U, C, G)
        """
        if 0 <= index < len(self.sequence):
            probability = self.mutation_probabilities.get(new_nucleotide.upper(), 0.5)
            if random.random() < probability:
                print(f"Mutated {self.sequence[index]} to {new_nucleotide} with probability {probability}.")
                self.sequence = self.sequence[:index] + new_nucleotide.upper() + self.sequence[index + 1:]
            else:
                print(f"Did not mutate {self.sequence[index]} with probability {probability}.")
        else:
            raise IndexError("Index out of range for mutation.")

    def simulate_rRNA_processing(self):
        """
        Simulate the processing of rRNA (cleavage of precursor into mature rRNA forms).
        For simplicity, we divide the sequence into regions corresponding to small and large subunit rRNA.

        :return: List of mature rRNA sequences after cleavage
        """
        # This is a simplification of real rRNA processing. In reality, specific cleavage sites are recognized.
        cleavage_sites = [100, 300, 600]  # Simplified cleavage sites
        fragments = []

        start = 0
        for site in cleavage_sites:
            fragments.append(self.sequence[start:site])
            start = site
        fragments.append(self.sequence[start:])

        self.processed_rRNA = fragments
        return fragments

    def simulate_folding(self):
        """
        Simulate the folding of rRNA into a secondary structure.
        In reality, rRNA folds into complex shapes with stems and loops. Here, we'll simulate a simplified structure.
        :return: A list of stem-loop structures representing the folded rRNA
        """
        if not self.processed_rRNA:
            raise ValueError("rRNA must be processed before folding.")

        stems = self.find_stem_loop()
        return stems

    def gc_content(self):
        """
        Calculate the GC content of the rRNA sequence.
        rRNA typically has a higher GC content in certain regions, important for its structure.

        :return: The percentage of G and C nucleotides in the sequence
        """
        gc_count = self.sequence.count('G') + self.sequence.count('C')
        return (gc_count / len(self.sequence)) * 100

    def to_dict(self):
        """
        Convert the rRNA object to a dictionary.

        :return: Dictionary representation of the rRNA
        """
        return {'sequence': self.sequence, 'processed_rRNA': self.processed_rRNA}

    @classmethod
    def from_dict(cls, data):
        """
        Create an rRNA object from a dictionary.

        :param data: Dictionary containing rRNA data
        :return: rRNA object
        """
        obj = cls(data['sequence'])
        obj.processed_rRNA = data.get('processed_rRNA')
        return obj

    def to_json(self):
        """
        Convert the rRNA object to a JSON string.

        :return: JSON string representation of the rRNA
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str):
        """
        Create an rRNA object from a JSON string.

        :param json_str: JSON string containing rRNA data
        :return: rRNA object
        """
        return cls.from_dict(json.loads(json_str))

    def find_cleavage_sites(self):
        """
        Find and return positions of all cleavage sites in the RNA sequence.
        :return: List of cleavage site indices
        """
        cleavage_positions = []
        for site in self.cleavage_sites:
            start = 0
            while True:
                start = self.sequence.find(site, start)
                if start == -1:
                    break
                cleavage_positions.append(start)
                start += len(site)
        return cleavage_positions

    def cleave_at_sites(self):
        """
        Cleave the RNA at all known cleavage sites.
        :return: A list of RNA fragments
        """
        cleavage_positions = self.find_cleavage_sites()
        if not cleavage_positions:
            return [self.sequence]

        # Sort cleavage positions and cleave the RNA sequence
        fragments = []
        previous_position = 0
        for position in sorted(cleavage_positions):
            fragments.append(self.sequence[previous_position:position])
            previous_position = position
        fragments.append(self.sequence[previous_position:])
        return fragments

    def find_stem_loop(self, min_stem_length=4, max_loop_length=10):
        """
        Identify potential stem-loop structures in the RNA sequence.
        :param min_stem_length: Minimum length of the stem
        :param max_loop_length: Maximum length of the loop
        :return: List of tuples indicating the start and end of stem-loop structures
        """
        stems = []
        seq_len = len(self.sequence)
        for i in range(seq_len - min_stem_length - max_loop_length):
            for j in range(i + min_stem_length, seq_len - min_stem_length):
                # Check for potential complementary stem region
                stem1 = self.sequence[i:i + min_stem_length]
                stem2 = self.sequence[j:j + min_stem_length][::-1]  # Reverse complement

                if self.is_complementary(stem1, stem2):
                    loop_length = j - (i + min_stem_length)
                    if loop_length <= max_loop_length:
                        stems.append((i, i + min_stem_length + loop_length + min_stem_length))
        return stems

    def is_complementary(self, seq1, seq2):
        """
        Check if two sequences are complementary.
        :param seq1: First RNA sequence
        :param seq2: Second RNA sequence (should be reversed for proper comparison)
        :return: True if complementary, False otherwise
        """
        complement = {'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C'}
        return all(complement.get(base1, '') == base2 for base1, base2 in zip(seq1, seq2))

    def display_stem_loop_structure(self):
        """
        Display RNA sequence with potential stem-loop structures highlighted.
        :return: A representation of the RNA with stem-loop structures
        """
        stem_loops = self.find_stem_loop()
        if not stem_loops:
            return self.sequence

        display_sequence = list(self.sequence)
        for stem_start, stem_end in stem_loops:
            display_sequence[stem_start] = "("  # Start of stem
            display_sequence[stem_end - 1] = ")"  # End of stem
        return ''.join(display_sequence)

    def transcribe_to_mrna(self):
        """
        Transcribe the RNA sequence to mRNA, incorporating post-transcriptional modifications.

        :return: An mRNA object and the protein sequence
        """
        # Create an mRNA object from the RNA sequence
        mrna = mRNA(self.sequence)

        # Add cap and poly-A tail
        mrna.add_cap()
        mrna.add_poly_a_tail()

        utr_5 = self.sequence[:50]  # First 50 nucleotides as 5' UTR
        utr_3 = self.sequence[-100:]  # Last 100 nucleotides as 3' UTR
        mrna.set_utrs(utr_5, utr_3)

        # Set coding sequence
        mrna.set_coding_sequence()

        # Simulate ribosome binding and translation using tRNA
        protein_sequence = self.translate_using_trna(mrna.coding_sequence)

        return mrna, protein_sequence

    def translate_using_trna(self, coding_sequence):
        """
        Translate the coding sequence of mRNA into a protein sequence using tRNA.

        :param coding_sequence: The coding sequence of the mRNA
        :return: The protein sequence
        """
        protein_sequence = ""
        codon_table = {
            'UUU': 'F', 'UUC': 'F', 'UUA': 'L', 'UUG': 'L',
            'CUU': 'L', 'CUC': 'L', 'CUA': 'L', 'CUG': 'L',
            'AUU': 'I', 'AUC': 'I', 'AUA': 'I', 'AUG': 'M',
            'GUU': 'V', 'GUC': 'V', 'GUA': 'V', 'GUG': 'V',
            'UCU': 'S', 'UCC': 'S', 'UCA': 'S', 'UCG': 'S',
            'CCU': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
            'ACU': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
            'GCU': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
            'UAU': 'Y', 'UAC': 'Y', 'UAA': '*', 'UAG': '*',
            'CAU': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'AAU': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
            'GAU': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
            'UGU': 'C', 'UGC': 'C', 'UGA': '*', 'UGG': 'W',
            'CGU': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
            'AGU': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
            'GGU': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
        }

        for i in range(0, len(coding_sequence) - 2, 3):
            codon = coding_sequence[i:i + 3]
            amino_acid = codon_table.get(codon, 'X')  # 'X' for unknown amino acid
            if amino_acid == '*':
                break  # Stop translation at stop codon
            protein_sequence += amino_acid

        return protein_sequence

    def __str__(self):
        """
        Return a string representation of the rRNA.
        """
        return f"rRNA Sequence: {self.sequence[:50]}... (length: {len(self.sequence)})"

    def __len__(self):
        """
        Return the length of the rRNA sequence.
        """
        return len(self.sequence)

    def __eq__(self, other):
        """
        Check if two rRNA objects are equal.
        """
        if isinstance(other, rRNA):
            return self.sequence == other.sequence
        return False

    def __getitem__(self, index):
        """
        Allow indexing of the rRNA sequence.
        """
        return self.sequence[index]
