import random
import json
from biobridge.genes.mRNA import mRNA
from biobridge.blocks.protein import Protein
from biobridge.genes.rRNA import rRNA


class RNA:
    def __init__(self, sequence):
        """
        Initialize a new RNA object.

        :param sequence: The nucleotide sequence of the RNA strand
        """
        self.sequence = sequence.upper().replace('T', 'U')
        self.mutation_probabilities = {
            'A': 0.1, 'C': 0.2, 'G': 0.3, 'U': 0.4
        }
        self.ribosomes = []

    def absolute_mutate(self, index, new_nucleotide, probability):
        """
        Mutate the RNA sequence at a specific index with an absolute probability.
        :param index:
        :param new_nucleotide:
        :param probability:
        :return:
        """
        if random.random < probability:
            if 0 <= index < len(self.sequence):
                print(f"Mutated {self.sequence[index]} to {new_nucleotide} with probability {probability}.")
                self.sequence = self.sequence[:index] + new_nucleotide.upper() + self.sequence[index + 1:]
            else:
                print(f"Did not mutate {self.sequence[index]} with probability {probability}.")
        else:
            print(f"Index {index} out of range for mutation.")

    def mutate(self, index, new_nucleotide):
        """
        Mutate the RNA sequence at a specific index.

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
            print(f"Index {index} out of range for mutation.")

    def absolute_random_mutate(self, probability):
        """
        Randomly mutate the RNA sequence with an absolute probability.
        :return:
        """
        for i in range(len(self.sequence)):
            if random.random() < probability:
                new_nucleotide = random.choice(['A', 'U', 'C', 'G'])
                self.mutate(i, new_nucleotide)

    def random_mutate(self, mutation_rate=0.01):
        """
        Randomly mutate the RNA sequence.

        :param mutation_rate: Probability of mutation for each nucleotide (default 1%)
        """
        for i in range(len(self.sequence)):
            if random.random() < mutation_rate:
                new_nucleotide = random.choice(['A', 'U', 'C', 'G'])
                self.mutate(i, new_nucleotide)

    def transcribe_to_mrna(self):
        """
        Transcribe the RNA sequence to mRNA, incorporating post-transcriptional modifications.

        :return: An mRNA object and Protein object
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

        ribosome = rRNA(mrna.sequence, id=random.random())
        self.ribosomes.append(ribosome)

        # Simulate ribosome binding and translation using tRNA
        protein_sequence = self.translate_using_trna(mrna.coding_sequence)

        mrna.protein_sequence = protein_sequence

        return mrna

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

    def simulate_rna_processing(self):
        """
        Simulate RNA processing, including 5' capping, splicing, and 3' polyadenylation.

        :return: A processed RNA sequence
        """
        # 5' capping
        processed_sequence = "m7G" + self.sequence

        # Splicing (simplified)
        exons = self.identify_exons()
        processed_sequence = self.splice_sequence(processed_sequence, exons)

        # 3' polyadenylation
        processed_sequence += "A" * 200  # Add a poly-A tail of 200 nucleotides

        return processed_sequence

    def identify_exons(self):
        """
        Identify exons in the RNA sequence using a simple algorithm.
        In this example, we'll consider regions between stop codons as potential exons.

        :return: A list of tuples representing exon ranges (start, end)
        """
        stop_codons = ['UAA', 'UAG', 'UGA']
        exons = []
        start = 0
        for i in range(0, len(self.sequence) - 2, 3):
            if self.sequence[i:i + 3] in stop_codons:
                if i > start:
                    exons.append((start, i))
                start = i + 3
        if start < len(self.sequence):
            exons.append((start, len(self.sequence)))
        return exons

    def splice_sequence(self, sequence, exons):
        """
        Splice the sequence by keeping only the exon regions.

        :param sequence: The full RNA sequence
        :param exons: List of exon ranges
        :return: The spliced RNA sequence
        """
        return ''.join(sequence[start:end] for start, end in exons)

    def simulate_alternative_splicing(self):
        """
        Simulate alternative splicing by randomly including or excluding exons.

        :return: An alternatively spliced RNA sequence
        """
        exons = self.identify_exons()
        included_exons = [exons[0]]  # Always include the first exon

        for exon in exons[1:-1]:
            if random.random() < 0.7:  # 70% chance of including each middle exon
                included_exons.append(exon)

        included_exons.append(exons[-1])  # Always include the last exon

        return self.splice_sequence(self.sequence, included_exons)

    def create_rna_from_dna(self, dna_sequence):
        """
        Create an RNA sequence from a given DNA sequence.

        :param dna_sequence: The DNA sequence to transcribe
        :return: The transcribed RNA sequence
        """
        rna_sequence = dna_sequence.replace('T', 'U')
        self.sequence = rna_sequence
        return self.sequence

    def reverse_transcribe(self):
        """
        Reverse transcribe the RNA sequence into DNA (replace U with T).

        :return: The DNA sequence corresponding to the RNA
        """
        return self.sequence.replace('U', 'T')

    def advanced_reverse_transcribe(self):
        """
        Perform advanced reverse transcription from RNA to DNA.

        :return: A DNA sequence (string)
        """
        # Convert RNA to DNA sequence
        dna_sequence = self.sequence.replace('U', 'T')

        # Simulate reverse transcriptase errors
        error_rate = 0.001  # 0.1% error rate
        dna_sequence = self.introduce_rt_errors(dna_sequence, error_rate)

        # Simulate template switching
        dna_sequence = self.simulate_template_switching(dna_sequence)

        return dna_sequence

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

    def simulate_template_switching(self, sequence):
        """
        Simulate template switching during reverse transcription.

        :param sequence: The input DNA sequence
        :return: The sequence after potential template switching
        """
        switch_probability = 0.01  # 1% chance of template switching
        if random.random() < switch_probability:
            switch_point = random.randint(0, len(sequence) - 1)
            return sequence[:switch_point] + sequence[switch_point:][::-1]
        return sequence

    def reverse_transcribe_to_dna_with_priming(self, primer):
        """
        Perform reverse transcription with a specific primer.

        :param primer: The DNA primer sequence
        :return: A DNA sequence (string)
        """
        if not self.sequence.endswith(primer.replace('T', 'U')):
            raise ValueError("Primer does not match the 3' end of the RNA sequence")

        # Start reverse transcription from the primer
        dna_sequence = primer
        template = self.sequence[:-len(primer)][::-1].replace('U', 'T')

        for nucleotide in template:
            complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}[nucleotide]
            dna_sequence += complement

        return dna_sequence[::-1]  # Reverse the sequence to get 5' to 3' orientation

    def create_dna_from_rna(self):
        """
        Create a DNA sequence from the RNA sequence, simulating the full reverse transcription process.

        :return: A DNA sequence (string)
        """
        # Start with an RNA-dependent DNA polymerase (reverse transcriptase) step
        dna_sequence = self.advanced_reverse_transcribe()

        # Simulate RNase H activity to degrade the RNA template
        # (In reality, this happens concurrently with DNA synthesis, but we'll simulate it as a separate step)

        # Simulate DNA-dependent DNA polymerase activity to create the second DNA strand
        second_strand = ''
        for nucleotide in dna_sequence:
            complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}[nucleotide]
            second_strand += complement

        # The final DNA is double-stranded, but we'll return just one strand for simplicity
        return dna_sequence

    def translate(self):
        """
        Translate the RNA sequence into a protein sequence.

        :return: The protein sequence
        """
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

        protein = ""
        for i in range(0, len(self.sequence) - 2, 3):
            codon = self.sequence[i:i + 3]
            amino_acid = codon_table.get(codon, 'X')  # 'X' for unknown amino acid
            if amino_acid == '*':
                break  # Stop translation at stop codon
            protein += amino_acid
        return protein

    def find_start_codons(self):
        """
        Find all start codons (AUG) in the RNA sequence.

        :return: List of indices where start codons are found
        """
        return [i for i in range(len(self.sequence) - 2) if self.sequence[i:i + 3] == 'AUG']

    def find_stop_codons(self):
        """
        Find all stop codons (UAA, UAG, UGA) in the RNA sequence.

        :return: List of indices where stop codons are found
        """
        stop_codons = ['UAA', 'UAG', 'UGA']
        return [i for i in range(len(self.sequence) - 2) if self.sequence[i:i + 3] in stop_codons]

    def find_orfs(self):
        """
        Find all open reading frames (ORFs) in the RNA sequence.

        :return: List of tuples (start_index, end_index) for each ORF
        """
        start_codons = self.find_start_codons()
        stop_codons = self.find_stop_codons()
        orfs = []

        for start in start_codons:
            for stop in stop_codons:
                if stop > start and (stop - start) % 3 == 0:
                    orfs.append((start, stop + 3))
                    break

        return orfs

    def gc_content(self):
        """
        Calculate the GC content of the RNA sequence.

        :return: The percentage of G and C nucleotides in the sequence
        """
        gc_count = self.sequence.count('G') + self.sequence.count('C')
        return (gc_count / len(self.sequence)) * 100

    def find_motif(self, motif):
        """
        Find a specific motif in the RNA sequence.

        :param motif: The motif to search for
        :return: List of starting positions where the motif is found
        """
        return [i for i in range(len(self.sequence) - len(motif) + 1) if self.sequence[i:i + len(motif)] == motif]

    def protein_synthesis(self):
        """
        Simulate the process of protein synthesis using the ribosomes associated with this RNA.
        :return: A list of Protein objects synthesized from the RNA sequence.
        """
        synthesized_proteins = []
        for ribosome in self.ribosomes:
            mrna, protein_sequence = ribosome.transcribe_to_mrna()
            synthesized_protein = Protein(name=f"Translated_Protein_{ribosome.id}",
                                          sequence=protein_sequence)
            synthesized_proteins.append(synthesized_protein)
        return synthesized_proteins

    def to_dict(self):
        """
        Convert the RNA object to a dictionary.

        :return: Dictionary representation of the RNA
        """
        return {'sequence': self.sequence, 'ribosomes': self.ribosomes}

    @classmethod
    def from_dict(cls, data):
        """
        Create an RNA object from a dictionary.

        :param data: Dictionary containing RNA data
        :return: RNA object
        """
        return cls(data['sequence', 'ribosomes'])

    def to_json(self):
        """
        Convert the RNA object to a JSON string.

        :return: JSON string representation of the RNA
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str):
        """
        Create an RNA object from a JSON string.

        :param json_str: JSON string containing RNA data
        :return: RNA object
        """
        return cls.from_dict(json.loads(json_str))

    def __str__(self):
        """
        Return a string representation of the RNA.
        """
        return f"RNA Sequence: {self.sequence}"

    def __len__(self):
        """
        Return the length of the RNA sequence.
        """
        return len(self.sequence)

    def __eq__(self, other):
        """
        Check if two RNA objects are equal.
        """
        if isinstance(other, RNA):
            return self.sequence == other.sequence
        return False

    def __getitem__(self, index):
        """
        Allow indexing of the RNA sequence.
        """
        return self.sequence[index]
