from typing import List, Tuple
from biobridge.genes.dna import DNA
from biobridge.blocks.protein import Protein
from biobridge.blocks.cell import Cell


class BioinformaticsPipeline:
    @staticmethod
    def align_sequences(seq1: str, seq2: str) -> Tuple[str, str]:
        """
        Perform a simple global sequence alignment using the Needleman-Wunsch algorithm.

        :param seq1: First sequence to align
        :param seq2: Second sequence to align
        :return: Tuple of aligned sequences
        """
        m, n = len(seq1), len(seq2)
        score = [[0] * (n + 1) for _ in range(m + 1)]

        # Initialize the score matrix
        for i in range(m + 1):
            score[i][0] = -i
        for j in range(n + 1):
            score[0][j] = -j

        # Fill the score matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                match = score[i - 1][j - 1] + (1 if seq1[i - 1] == seq2[j - 1] else -1)
                delete = score[i - 1][j] - 1
                insert = score[i][j - 1] - 1
                score[i][j] = max(match, delete, insert)

        # Traceback
        align1, align2 = "", ""
        i, j = m, n
        while i > 0 and j > 0:
            score_current = score[i][j]
            score_diagonal = score[i - 1][j - 1]
            if score_current == score_diagonal + (1 if seq1[i - 1] == seq2[j - 1] else -1):
                align1 = seq1[i - 1] + align1
                align2 = seq2[j - 1] + align2
                i -= 1
                j -= 1
            elif score_current == score[i - 1][j] - 1:
                align1 = seq1[i - 1] + align1
                align2 = '-' + align2
                i -= 1
            else:
                align1 = '-' + align1
                align2 = seq2[j - 1] + align2
                j -= 1

        while i > 0:
            align1 = seq1[i - 1] + align1
            align2 = '-' + align2
            i -= 1
        while j > 0:
            align1 = '-' + align1
            align2 = seq2[j - 1] + align2
            j -= 1

        return align1, align2

    @staticmethod
    def transcribe_dna(dna_sequence: str) -> str:
        """
        Transcribe a DNA sequence to RNA.

        :param dna_sequence: DNA sequence to transcribe
        :return: Transcribed RNA sequence
        """
        return dna_sequence.replace('T', 'U')

    @staticmethod
    def translate_rna(rna_sequence: str) -> str:
        """
        Translate an RNA sequence to a protein sequence.

        :param rna_sequence: RNA sequence to translate
        :return: Protein sequence
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

        protein_sequence = ""
        for i in range(0, len(rna_sequence) - 2, 3):
            codon = rna_sequence[i:i + 3]
            if len(codon) == 3:
                amino_acid = codon_table.get(codon, 'X')
                if amino_acid == '*':
                    break
                protein_sequence += amino_acid

        return protein_sequence

    @staticmethod
    def find_mutations(seq1: str, seq2: str) -> List[Tuple[int, str, str]]:
        """
        Find mutations between two aligned sequences.

        :param seq1: First sequence
        :param seq2: Second sequence
        :return: List of tuples (position, nucleotide in seq1, nucleotide in seq2)
        """
        mutations = []
        for i, (n1, n2) in enumerate(zip(seq1, seq2)):
            if n1 != n2:
                mutations.append((i, n1, n2))
        return mutations

    @staticmethod
    def simulate_evolution(dna: DNA, generations: int, mutation_rate: float) -> DNA:
        """
        Simulate evolution of a DNA sequence over multiple generations.

        :param dna: Initial DNA object
        :param generations: Number of generations to simulate
        :param mutation_rate: Probability of mutation per nucleotide
        :return: Evolved DNA object
        """
        evolved_dna = dna
        for _ in range(generations):
            evolved_dna = evolved_dna.replicate()
            evolved_dna.absolute_random_mutate(mutation_rate)
        return evolved_dna

    @staticmethod
    def analyze_protein_interactions(protein: Protein, cell: Cell) -> str:
        """
        Analyze interactions between a protein and a cell.

        :param protein: Protein object
        :param cell: Cell object
        :return: Description of interactions
        """
        interaction_result = f"{protein.name} interacting with {cell.name}:\n"

        # Check receptor bindings
        bound_receptors = [binding['site'] for binding in protein.bindings if binding['site'] in cell.receptors]
        if bound_receptors:
            interaction_result += f"- Binding to receptors: {', '.join(bound_receptors)}\n"
        else:
            interaction_result += "- No specific receptor binding detected\n"

        # Check surface protein interactions
        interacting_surface_proteins = [sp for sp in cell.surface_proteins if sp in protein.sequence]
        if interacting_surface_proteins:
            interaction_result += f"- Interacting with surface proteins: {', '.join(interacting_surface_proteins)}\n"
        else:
            interaction_result += "- No specific surface protein interaction detected\n"

        # Analyze protein activity
        activity_score = protein.activeness()
        interaction_result += f"- Protein activity score: {activity_score:.2f}\n"

        return interaction_result
