import random
import re
from collections import Counter
import json
from matplotlib import pyplot as plt
import numpy as np
from biobridge.genes.mRNA import mRNA
from biobridge.genes.rna import RNA
from biobridge.genes.gene import Gene


class Nucleotide:
    def __init__(self, base):
        self.base = base.upper()
        if self.base not in ['A', 'T', 'C', 'G']:
            raise ValueError("Invalid nucleotide base. Must be A, T, C, or G.")

    def complement(self):
        complements = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        return Nucleotide(complements[self.base])

    def __str__(self):
        return self.base

    def __eq__(self, other):
        if isinstance(other, Nucleotide):
            return self.base == other.base
        return False


class GeneEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Gene):
            return {
                'gene_name': obj.name,
                'start': obj.start,
                'end': obj.end
            }
        return super().default(obj)


class DNA:
    def __init__(self, sequence, genes=None):
        """
        Initialize a new DNA object.

        :param sequence: The nucleotide sequence of the DNA strand
        :param genes: A list of genes (optional), each represented by a tuple (gene_name, start_index, end_index)
        """
        self.strand1 = [Nucleotide(base) for base in sequence.upper()]
        self.strand2 = [nucleotide.complement() for nucleotide in self.strand1]
        self.genes = genes or []
        self.mutation_probabilities = {
            'A': 0.1, 'C': 0.2, 'D': 0.3, 'E': 0.4, 'F': 0.5,
            'G': 0.6, 'H': 0.7, 'I': 0.8, 'K': 0.9, 'L': 0.1,
            'M': 0.2, 'N': 0.3, 'P': 0.4, 'Q': 0.5, 'R': 0.6,
            'S': 0.7, 'T': 0.8, 'V': 0.9, 'W': 0.1, 'Y': 0.2
        }
        self.sequence = self.get_sequence(1)
        self.nucleotide_weights = {
            'A': 331.2,
            'T': 322.2,
            'C': 307.2,
            'G': 347.2
        }

    def add_gene(self, name, sequence, inheritance):
        """
        Add a gene to the DNA sequence and encode it into the sequence.

        :param name: The name of the gene
        :param sequence: The nucleotide sequence of the gene
        :param inheritance: The inheritance pattern of the gene
        """
        # Convert sequence to uppercase
        sequence = sequence.upper()

        # Find a suitable position to insert the gene
        insertion_point = self._find_insertion_point(len(sequence))

        # Update the DNA sequence
        new_sequence = (
            self.get_sequence(1)[:insertion_point] +
            sequence +
            self.get_sequence(1)[insertion_point:]
        )
        self.strand1 = [Nucleotide(base) for base in new_sequence]
        self.strand2 = [nucleotide.complement() for nucleotide in self.strand1]

        # Add the gene to the list
        new_gene = Gene(name, insertion_point, insertion_point + len(sequence), inheritance)
        self.genes.append(new_gene)

        # Adjust the positions of existing genes
        for gene in self.genes[:-1]:  # Exclude the newly added gene
            if gene.start >= insertion_point:
                gene.start += len(sequence)
                gene.end += len(sequence)

        print(f"Gene '{name}' added and encoded into the DNA sequence at position {insertion_point}.")

    def _find_insertion_point(self, gene_length):
        """
        Find a suitable insertion point for a new gene.

        :param gene_length: The length of the gene to be inserted
        :return: The index where the gene can be inserted
        """
        if not self.genes:
            return 0  # If no genes exist, insert at the beginning

        # Sort genes by their start position
        sorted_genes = sorted(self.genes, key=lambda g: g.start)

        # Check for space between genes
        for i in range(len(sorted_genes)):
            if i == 0:
                if sorted_genes[i].start >= gene_length:
                    return 0
            else:
                space = sorted_genes[i].start - sorted_genes[i-1].end
                if space >= gene_length:
                    return sorted_genes[i-1].end

        # If no suitable space found, append to the end
        return len(self.strand1)

    def remove_gene(self, name):
        """
        Remove a gene from the DNA sequence.

        :param name: The name of the gene to remove
        """
        # Find the gene to remove
        gene_to_remove = None
        for gene in self.genes:
            if gene.name == name:
                gene_to_remove = gene
                break

        if gene_to_remove:
            # Update the DNA sequence to remove the gene
            new_sequence = (
                self.get_sequence(1)[:gene_to_remove.start] +
                self.get_sequence(1)[gene_to_remove.end:]
            )
            self.strand1 = [Nucleotide(base) for base in new_sequence]
            self.strand2 = [nucleotide.complement() for nucleotide in self.strand1]

            # Remove the gene from the list
            self.genes.remove(gene_to_remove)

            # Adjust the positions of remaining genes
            for gene in self.genes:
                if gene.start > gene_to_remove.start:
                    gene.start -= gene_to_remove.end - gene_to_remove.start
                    gene.end -= gene_to_remove.end - gene_to_remove.start

            print(f"Gene '{name}' removed from the DNA sequence.")
        else:
            print(f"Gene '{name}' not found in the DNA sequence.")

    def absolute_mutate(self, index, new_nucleotide, probability):
        """
        Mutate the DNA sequence at a specific index with an absolute probability.
        :param index:
        :param new_nucleotide:
        :param probability:
        :return:
        """
        if random.random < probability:
            if 0 <= index < len(self.strand1):
                print(f"Mutated {self.strand1[index]} to {new_nucleotide} with probability {probability}.")
                self.strand1 = self.strand1[:index] + new_nucleotide.upper() + self.strand1[index + 1:]
                self.strand2[index] = self.strand1[index].complement()
            else:
                print(f"Did not mutate {self.strand1[index]} with probability {probability}.")
        else:
            print(f"Index {index} out of range for mutation.")

    def mutate(self, index, new_base):
        """
        Mutate the DNA sequence at a specific index.

        :param index: The position in the sequence to mutate
        :param new_base: The new base (A, T, C, G)
        """
        if 0 <= index < len(self.strand1):
            probability = self.mutation_probabilities.get(new_base.upper(), 0.5)
            if random.random() < probability:
                old_base = str(self.strand1[index])
                self.strand1[index] = Nucleotide(new_base.upper())
                self.strand2[index] = self.strand1[index].complement()
                print(f"Mutated {old_base} to {new_base} with probability {probability}.")
            else:
                print(f"Did not mutate {self.strand1[index]} with probability {probability}.")
        else:
            print(f"Index {index} out of range for mutation.")

    def absolute_random_mutate(self, probability):
        """
        Randomly mutate the DNA sequence with an absolute probability.
        """
        nucleotides = "ACGT"  # All possible nucleotides
        for i in range(len(self.strand1)):
            if random.random() < probability:
                print(f"Mutated {self.strand1[i]} to {random.choice(nucleotides)} with probability {probability}.")
                new_nucleotide = random.choice(nucleotides)
                self.mutate(i, new_nucleotide)
            else:
                print(f"Did not mutate {self.strand1[i]} with probability {probability}.")

    def get_sequence(self, strand=1):
        """
        Get the sequence of a specific strand.

        :param strand: 1 for the primary strand, 2 for the complementary strand
        :return: The sequence as a string
        """
        if strand == 1:
            return ''.join(str(nucleotide) for nucleotide in self.strand1)
        elif strand == 2:
            return ''.join(str(nucleotide) for nucleotide in self.strand2)
        else:
            raise ValueError("Invalid strand number. Must be 1 or 2.")

    def transcribe(self):
        """
        Transcribe the DNA sequence into RNA (replace T with U).

        :return: The RNA sequence corresponding to the DNA
        """
        return ''.join('U' if nucleotide.base == 'T' else str(nucleotide) for nucleotide in self.strand1)

    def advanced_transcribe(self, start=0, end=None):
        """
        Perform advanced transcription of DNA to RNA, incorporating splicing.

        :param start: Start index for transcription (default is 0)
        :param end: End index for transcription (default is None, which means end of sequence)
        :return: An RNA object
        """
        if end is None:
            end = len(self.strand1)

        # Transcribe the DNA sequence to pre-mRNA
        pre_mrna_sequence = ''.join(str(nucleotide) for nucleotide in self.strand1[start:end]).replace('T', 'U')

        # Simulate splicing
        exons = self.identify_exons(pre_mrna_sequence)
        spliced_sequence = self.splice_sequence(pre_mrna_sequence, exons)

        # Create and return an RNA object
        return RNA(spliced_sequence)

    def identify_exons(self, sequence):
        """
        Identify exons in the given sequence using a simple algorithm.
        In this example, we'll consider regions between stop codons as potential exons.

        :param sequence: The RNA sequence to analyze
        :return: A list of tuples representing exon ranges (start, end)
        """
        stop_codons = ['UAA', 'UAG', 'UGA']
        exons = []
        start = 0
        for i in range(0, len(sequence) - 2, 3):
            if sequence[i:i + 3] in stop_codons:
                if i > start:
                    exons.append((start, i))
                start = i + 3
        if start < len(sequence):
            exons.append((start, len(sequence)))
        return exons

    def splice_sequence(self, sequence, exons):
        """
        Splice the sequence by keeping only the exon regions.

        :param sequence: The full RNA sequence
        :param exons: List of exon ranges
        :return: The spliced RNA sequence
        """
        return ''.join(sequence[start:end] for start, end in exons)

    def construct_mrna(self, start=0, end=None):
        """
        Construct an mRNA object from the DNA sequence.

        :param start: Start index for transcription (default is 0)
        :param end: End index for transcription (default is None, which means end of sequence)
        :return: An mRNA object
        """
        if end is None:
            end = len(self.strand1)

        # Transcribe the DNA sequence to pre-mRNA
        pre_mrna_sequence = ''.join(str(nucleotide) for nucleotide in self.strand1[start:end]).replace('T', 'U')

        # Create an mRNA object
        mrna = mRNA(pre_mrna_sequence)

        # Add cap and poly-A tail
        mrna.add_cap()
        mrna.add_poly_a_tail()

        # Set UTRs (simplified example)
        utr_5 = pre_mrna_sequence[:50]  # First 50 nucleotides as 5' UTR
        utr_3 = pre_mrna_sequence[-100:]  # Last 100 nucleotides as 3' UTR
        mrna.set_utrs(utr_5, utr_3)

        # Set coding sequence
        mrna.set_coding_sequence()

        return mrna

    def transcribe_with_regulation(self, start=0, end=None, promoter_strength=1.0, enhancers=None, silencers=None):
        """
        Perform transcription with regulatory elements.

        :param start: Start index for transcription (default is 0)
        :param end: End index for transcription (default is None, which means end of sequence)
        :param promoter_strength: Strength of the promoter (0.0 to 1.0)
        :param enhancers: List of (position, strength) tuples for enhancers
        :param silencers: List of (position, strength) tuples for silencers
        :return: An RNA object with regulated expression
        """
        if end is None:
            end = len(self.strand1)

        # Calculate overall transcription rate
        rate = promoter_strength

        # Apply enhancer effects
        if enhancers:
            for position, strength in enhancers:
                if start <= position < end:
                    rate += strength

        # Apply silencer effects
        if silencers:
            for position, strength in silencers:
                if start <= position < end:
                    rate -= strength

        # Ensure rate is between 0 and 1
        rate = max(0, min(1, int(rate)))

        # Transcribe based on the calculated rate
        if random.random() < rate:
            return self.advanced_transcribe(start, end)
        else:
            return None  # Transcription did not occur

    def advanced_reverse_transcribe(self, rna):
        """
        Perform advanced reverse transcription from RNA to DNA.

        :param rna: An RNA object
        :return: A new DNA object
        """
        # Remove any RNA-specific modifications
        dna_sequence = rna.sequence.replace('U', 'T')

        # Simulate potential errors in reverse transcription
        error_rate = 0.001  # 0.1% error rate
        dna_sequence = self.introduce_rt_errors(dna_sequence, error_rate)

        # Create a new DNA object
        new_dna = DNA(dna_sequence)

        # Attempt to identify genes based on open reading frames
        new_dna.identify_potential_genes()

        return new_dna

    def introduce_rt_errors(self, sequence, error_rate):
        """
        Introduce errors into the sequence to simulate reverse transcription errors.

        :param sequence: The input sequence
        :param error_rate: The probability of an error at each position
        :return: The sequence with introduced errors
        """
        nucleotides = ['A', 'T', 'C', 'G']
        error_sequence = list(sequence)
        for i in range(len(error_sequence)):
            if random.random() < error_rate:
                error_sequence[i] = random.choice([n for n in nucleotides if n != error_sequence[i]])
        return ''.join(error_sequence)

    def identify_potential_genes(self):
        """
        Identify potential genes in the DNA sequence based on open reading frames.
        """
        start_codon = 'ATG'
        stop_codons = ['TAA', 'TAG', 'TGA']
        min_gene_length = 100  # Minimum length of a gene in nucleotides

        sequence = self.get_sequence(1)
        potential_genes = []

        for frame in range(3):
            start = None
            for i in range(frame, len(sequence) - 2, 3):
                codon = sequence[i:i + 3]
                if codon == start_codon and start is None:
                    start = i
                elif codon in stop_codons and start is not None:
                    if i + 3 - start >= min_gene_length:
                        potential_genes.append(('Unknown', start, i + 3))
                    start = None

        self.genes = potential_genes

    def reverse_transcribe_from_mrna(self, mrna):
        """
        Perform reverse transcription from mRNA to DNA.

        :param mrna: An mRNA object
        :return: A new DNA object
        """
        # Remove mRNA-specific features
        dna_sequence = mrna.sequence.replace('U', 'T')
        dna_sequence = dna_sequence[len(mrna.cap):]  # Remove 5' cap
        dna_sequence = dna_sequence[:-len(mrna.poly_a_tail)]  # Remove poly-A tail

        # Create a new DNA object
        new_dna = DNA(dna_sequence)

        # Identify potential genes based on the coding sequence
        if mrna.coding_sequence:
            start = dna_sequence.index(mrna.coding_sequence.replace('U', 'T'))
            end = start + len(mrna.coding_sequence)
            new_dna.genes = [('Unknown', start, end)]

        return new_dna

    def describe(self):
        """
        Provide a detailed description of the DNA, including its sequence and genes.
        """
        description = f"DNA Sequence (Strand 1): {self.get_sequence(1)}\n"
        description += f"Complementary Sequence (Strand 2): {self.get_sequence(2)}\n"
        if self.genes:
            description += "Genes:\n"
            for gene in self.genes:
                gene_sequence = self.get_sequence(1)[gene.start:gene.end]
                description += f"  {gene.name}: {gene_sequence} (Position: {gene.start}-{gene.end})\n"
        else:
            description += "No genes defined.\n"
        return description

    def random_mutate(self):
        """
        Randomly mutate the DNA sequence.
        """
        for i in range(len(self.strand1)):
            current_base = str(self.strand1[i])
            probability = self.mutation_probabilities.get(current_base, 0.5)
            if random.random() < probability:
                new_base = random.choice(['A', 'T', 'C', 'G'])
                self.mutate(i, new_base)

    def find_repeats(self, min_length=2):
        """
        Find repeated sequences in the DNA.

        :param min_length: Minimum length of repeat to consider
        :return: Dictionary of repeated sequences and their counts
        """
        sequence = self.get_sequence(1)
        repeats = {}
        for length in range(min_length, len(sequence) // 2 + 1):
            for i in range(len(sequence) - length + 1):
                substr = sequence[i:i + length]
                if sequence.count(substr) > 1:
                    repeats[substr] = sequence.count(substr)
        return repeats

    def find_palindromes(self, min_length=4):
        """
        Find palindromic sequences in the DNA.

        :param min_length: Minimum length of palindrome to consider
        :return: List of palindromic sequences
        """
        sequence = self.get_sequence(1)
        palindromes = []
        for i in range(len(sequence)):
            for j in range(i + min_length, len(sequence) + 1):
                substr = sequence[i:j]
                if substr == substr[::-1]:
                    palindromes.append(substr)
        return palindromes

    def gc_content(self):
        """
        Calculate the GC content of the DNA sequence.

        :return: Percentage of G and C nucleotides in the sequence
        """
        sequence = self.get_sequence(1)
        gc_count = sequence.count('G') + sequence.count('C')
        return (gc_count / len(sequence)) * 100

    def find_motif(self, motif):
        """
        Find occurrences of a specific motif in the DNA sequence.

        :param motif: The motif to search for
        :return: List of starting positions of the motif
        """
        sequence = self.get_sequence(1)
        return [m.start() for m in re.finditer(f'(?={motif})', sequence)]

    def codon_usage(self):
        """
        Calculate the codon usage in the DNA sequence.

        :return: Dictionary of codons and their frequencies
        """
        sequence = self.get_sequence(1)
        codons = {}
        for i in range(0, len(sequence) - 2, 3):
            codon = sequence[i:i + 3]
            codons[codon] = codons.get(codon, 0) + 1
        return codons

    def translate(self, start=0, end=None):
        """
        Translate the DNA sequence into an amino acid sequence.

        :param start: Start index for translation (default is 0)
        :param end: End index for translation (default is None, which means end of sequence)
        :return: The amino acid sequence
        """
        if end is None:
            end = len(self.strand1)

        codon_table = {
            'ATA': 'I', 'ATC': 'I', 'ATT': 'I', 'ATG': 'M',
            'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T',
            'AAC': 'N', 'AAT': 'N', 'AAA': 'K', 'AAG': 'K',
            'AGC': 'S', 'AGT': 'S', 'AGA': 'R', 'AGG': 'R',
            'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L',
            'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P',
            'CAC': 'H', 'CAT': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
            'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V',
            'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A',
            'GAC': 'D', 'GAT': 'D', 'GAA': 'E', 'GAG': 'E',
            'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G',
            'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
            'TTC': 'F', 'TTT': 'F', 'TTA': 'L', 'TTG': 'L',
            'TAC': 'Y', 'TAT': 'Y', 'TAA': '_', 'TAG': '_',
            'TGC': 'C', 'TGT': 'C', 'TGA': '_', 'TGG': 'W',
        }

        sequence = self.get_sequence(1)
        protein = ""
        for i in range(start, end, 3):
            codon = sequence[i:i + 3]
            if len(codon) == 3:
                amino_acid = codon_table.get(codon, 'X')  # 'X' for unknown amino acid
                if amino_acid == '_':  # Stop codon
                    break
                protein += amino_acid

        return protein

    def find_orfs(self, min_length=100):
        """
        Find all open reading frames (ORFs) in the DNA sequence.

        :param min_length: Minimum length of ORF to consider (in nucleotides)
        :return: List of ORFs, each represented by a tuple (start_index, end_index, amino_acid_sequence)
        """
        sequence = self.get_sequence(1)
        orfs = []
        start_codons = ['ATG']
        stop_codons = ['TAA', 'TAG', 'TGA']

        for frame in range(3):
            start = None
            for i in range(frame, len(sequence) - 2, 3):
                codon = sequence[i:i + 3]
                if codon in start_codons and start is None:
                    start = i
                elif codon in stop_codons and start is not None:
                    if i - start >= min_length:
                        orf_sequence = self.translate(start, i + 3)
                        orfs.append((start, i + 3, orf_sequence))
                    start = None

        return orfs

    def calculate_nucleotide_frequency(self):
        """
        Calculate the frequency of each nucleotide in the DNA sequence.

        :return: Dictionary with nucleotide frequencies
        """
        sequence = self.get_sequence(1)
        return dict(Counter(sequence))

    def hamming_distance(self, other_dna):
        """
        Calculate the Hamming distance between this DNA sequence and another.

        :param other_dna: Another DNA object to compare with
        :return: The Hamming distance (number of positions at which nucleotides differ)
        """
        if len(self.strand1) != len(other_dna.strand1):
            raise ValueError("Sequences must be of equal length")

        return sum(s1 != s2 for s1, s2 in zip(self.strand1, other_dna.strand1))

    def find_restriction_sites(self, enzyme_sites):
        """
        Find restriction enzyme cut sites in the DNA sequence.

        :param enzyme_sites: Dictionary of enzyme names and their recognition sequences
        :return: Dictionary of enzyme names and lists of cut site positions
        """
        cut_sites = {}
        for enzyme, site in enzyme_sites.items():
            cut_sites[enzyme] = self.find_motif(site)
        return cut_sites

    def encode_8bit(self, input_data):
        """
        Encode general input data (including letters and other characters) into the DNA sequence.
        :param input_data: A string of any characters
        :return: The DNA sequence representing the input data
        """
        # Convert each character to its ASCII binary representation, then to DNA sequence
        encoding = {'00': 'A', '01': 'C', '10': 'G', '11': 'T'}
        dna_sequence = ''
        for char in input_data:
            binary_repr = format(ord(char), '08b')  # Get 8-bit binary representation of ASCII value
            for i in range(0, len(binary_repr), 2):
                pair = binary_repr[i:i + 2]
                dna_sequence += encoding[pair]
        return dna_sequence

    def decode_8bit(self, dna_sequence):
        """
        Decode a DNA sequence back into the original string.
        :param dna_sequence: A DNA sequence string
        :return: The original data string
        """
        decoding = {'A': '00', 'C': '01', 'G': '10', 'T': '11'}
        binary_data = ''
        for char in dna_sequence:
            binary_data += decoding[char]

        # Split binary data into 8-bit chunks and convert to characters
        original_data = ''
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i + 8]
            original_data += chr(int(byte, 2))
        return original_data

    def encode_binary(self, binary_data):
        """
        Encode binary data into the DNA sequence.
        :param binary_data: A string of 0s and 1s
        :return: The DNA sequence representing the binary data
        """
        encoding = {'00': 'A', '01': 'C', '10': 'G', '11': 'T'}
        dna_sequence = ''
        for i in range(0, len(binary_data), 2):
            if i + 1 < len(binary_data):
                pair = binary_data[i:i + 2]
                dna_sequence += encoding[pair]
            else:
                # If there's an odd number of bits, pad with 0
                dna_sequence += encoding[binary_data[i] + '0']
        return dna_sequence

    def decode_binary(self):
        """
        Decode the DNA sequence back into binary data.

        :return: The binary data as a string of 0s and 1s
        """
        decoding = {'A': '00', 'C': '01', 'G': '10', 'T': '11'}
        binary_data = ''
        for nucleotide in self.strand1:
            binary_data += decoding[nucleotide]
        return binary_data

    def store_binary_data(self, binary_data):
        """
        Store binary data in the DNA sequence.

        :param binary_data: A string of 0s and 1s
        """
        self.strand1 = self.encode_binary(binary_data)

    def retrieve_binary_data(self):
        """
        Retrieve the stored binary data from the DNA sequence.

        :return: The binary data as a string of 0s and 1s
        """
        return self.decode_binary()

    def replicate(self, mutation_rate=0.001):
        """
        Simulate DNA replication, potentially introducing mutations.

        :param mutation_rate: The probability of a mutation occurring at each nucleotide (default is 0.001)
        :return: A new DNA object representing the replicated DNA strand
        """
        new_sequence = ""
        mutations = 0
        for nucleotide in self.strand1:
            if random.random() < mutation_rate:
                new_base = random.choice(['A', 'T', 'C', 'G'])
                if new_base != str(nucleotide):
                    mutations += 1
                new_sequence += new_base
            else:
                new_sequence += str(nucleotide)

        new_dna = DNA(new_sequence, self.genes.copy())

        print(f"DNA replication complete. {mutations} mutations occurred.")
        return new_dna

    def to_dict(self) -> dict:
        return {
            'sequence': self.get_sequence(1),
            'genes': self.genes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DNA':
        return cls(data['sequence'], data['genes'])

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), cls=GeneEncoder)

    @classmethod
    def from_json(cls, json_str: str) -> 'DNA':
        return cls.from_dict(json.loads(json_str))

    def get_genes(self):
        return self.genes

    def create_gene_heatmap(self):
        """
        Create a heatmap visualization of the genes in the DNA object.
        """
        # Get the gene information from the DNA object
        genes = self.get_genes()

        # Create a matrix to store the gene presence/absence data
        matrix = np.zeros((len(genes), len(self.strand1)))

        # Populate the matrix with 1s for the gene regions
        for i, gene in enumerate(genes):
            matrix[i, gene.start:gene.end] = 1

        # Create the heatmap
        fig, ax = plt.subplots(figsize=(12, 6))
        heatmap = ax.imshow(matrix.T, cmap='binary', aspect='auto')

        # Add labels and title
        ax.set_xlabel('Nucleotide Position')
        ax.set_ylabel('Gene')
        ax.set_title('Heatmap of Genes in DNA Sequence')

        # Add a colorbar
        cbar = fig.colorbar(heatmap, ax=ax)
        cbar.ax.set_ylabel('Gene Presence')

        # Add gene names in the center of the gene regions
        for i, gene in enumerate(genes):
            # Compute the center of the gene region for labeling
            center_position = (gene.start + gene.end) // 2
            ax.text(i, center_position, gene.name, ha='center', va='center', fontsize=12, color='white', rotation=0)

        # Adjust the spacing between subplots
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

        # Display the heatmap
        plt.show()

    def has_mutation(self):
        """
        Check if the DNA sequence has any mutations.
        """
        return 'mutation' in self.get_sequence(1)

    def calculate_molecular_weight(self):
        """
        Calculate the molecular weight of the DNA based on its sequence and genes.

        :return: A tuple containing (total_weight, gene_weights)
            - total_weight: The total molecular weight of the DNA (in g/mol)
            - gene_weights: A dictionary of gene names and their molecular weights
        """
        total_weight = 0
        gene_weights = {}

        # Calculate weight for the entire DNA sequence
        for nucleotide in self.get_sequence(1):
            total_weight += self.nucleotide_weights.get(nucleotide, 0)

        # Calculate weights for individual genes
        for gene in self.genes:
            gene_sequence = self.get_sequence(1)[gene.start:gene.end]
            gene_weight = sum(self.nucleotide_weights.get(n, 0) for n in gene_sequence)
            gene_weights[gene.name] = gene_weight

        # Each nucleotide contributes about 178.4 g/mol for the backbone
        backbone_weight = len(self.get_sequence(1)) * 178.4
        total_weight += backbone_weight

        return total_weight, gene_weights

    def display_molecular_weights(self):
        """
        Display the molecular weights of the DNA and its genes.
        """
        total_weight, gene_weights = self.calculate_molecular_weight()

        print(f"Total molecular weight of DNA: {total_weight:.2f} g/mol")
        print("\nMolecular weights of genes:")
        for gene_name, weight in gene_weights.items():
            print(f"{gene_name}: {weight:.2f} g/mol")

    def __len__(self):
        """
        Return the length of the DNA sequence.
        """
        return len(self.strand1) + len(self.strand2)

    def __getitem__(self, index):
        """
        Allow indexing of the DNA sequence.
        """
        return self.get_sequence(1)[index]

    def __eq__(self, other):
        """
        Check if two DNA sequences are equal.
        """
        if isinstance(other, DNA):
            return self.strand1 == other.strand1
        return False

    def __str__(self):
        """
        Return a string representation of the DNA.
        """
        return self.describe()
