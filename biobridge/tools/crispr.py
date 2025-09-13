import random
from typing import List, Tuple
from biobridge.genes.dna import DNA


class CRISPR:
    def __init__(self, guide_rna: str):
        self.guide_rna = guide_rna.upper()

    def find_target_sequence(self, dna: 'DNA') -> List[int]:
        """
        Find all occurrences of the target sequence in the DNA.

        :param dna: The DNA object to search in
        :return: List of starting indices of the target sequence
        """
        return [i for i in range(len(dna.strand1) - len(self.guide_rna) + 1)
                if dna.strand1[i:i + len(self.guide_rna)] == self.guide_rna]

    def cut_dna(self, dna: 'DNA', index: int) -> Tuple['DNA', 'DNA']:
        """
        Simulate cutting the DNA at the specified index.

        :param dna: The DNA object to cut
        :param index: The index at which to cut the DNA
        :return: Two DNA objects representing the cut fragments
        """
        left_fragment = DNA(dna.sequence[:index])
        right_fragment = DNA(dna.sequence[index:])
        return left_fragment, right_fragment

    def insert_sequence(self, dna: 'DNA', insert_seq: str, index: int) -> 'DNA':
        """
        Insert a sequence into the DNA at the specified index.

        :param dna: The DNA object to modify
        :param insert_seq: The sequence to insert
        :param index: The index at which to insert the sequence
        :return: A new DNA object with the inserted sequence
        """
        new_sequence = dna.sequence[:index] + insert_seq + dna.sequence[index:]
        return DNA(new_sequence)

    def delete_sequence(self, dna: 'DNA', start: int, end: int) -> 'DNA':
        """
        Delete a sequence from the DNA between the specified indices.

        :param dna: The DNA object to modify
        :param start: The starting index of the sequence to delete
        :param end: The ending index of the sequence to delete
        :return: A new DNA object with the sequence deleted
        """
        new_sequence = dna.sequence[:start] + dna.sequence[end:]
        return DNA(new_sequence)

    def replace_sequence(self, dna: 'DNA', replacement: str, start: int, end: int) -> 'DNA':
        """
        Replace a sequence in the DNA with a new sequence.

        :param dna: The DNA object to modify
        :param replacement: The replacement sequence
        :param start: The starting index of the sequence to replace
        :param end: The ending index of the sequence to replace
        :return: A new DNA object with the replaced sequence
        """
        new_sequence = dna.sequence[:start] + replacement + dna.sequence[end:]
        return DNA(new_sequence)

    def edit_genome(self, dna: 'DNA', edit_type: str, *args) -> 'DNA':
        """
        Perform a CRISPR edit on the DNA.

        :param dna: The DNA object to edit
        :param edit_type: The type of edit to perform ('insert', 'delete', or 'replace')
        :param args: Additional arguments specific to the edit type
        :return: A new DNA object with the edit applied
        """
        target_sites = self.find_target_sequence(dna)
        if not target_sites:
            print("No target site found for the guide RNA.")
            return dna

        # Choose a random target site if multiple are found
        edit_site = random.choice(target_sites)

        if edit_type == 'insert':
            insert_seq = args[0]
            return self.insert_sequence(dna, insert_seq, edit_site + len(self.guide_rna))
        elif edit_type == 'delete':
            delete_length = args[0]
            return self.delete_sequence(dna, edit_site, edit_site + delete_length)
        elif edit_type == 'replace':
            replacement = args[0]
            return self.replace_sequence(dna, replacement, edit_site, edit_site + len(self.guide_rna))
        else:
            raise ValueError("Invalid edit type. Choose 'insert', 'delete', or 'replace'.")

    def simulate_off_target_effects(self, dna: 'DNA', mutation_rate: float = 0.1) -> 'DNA':
        """
        Simulate off-target effects of CRISPR editing.

        :param dna: The DNA object to potentially modify
        :param mutation_rate: The probability of an off-target mutation occurring
        :return: A potentially modified DNA object
        """
        if random.random() < mutation_rate:
            mutation_site = random.randint(0, len(dna.sequence) - 1)
            new_base = random.choice(['A', 'T', 'C', 'G'])
            new_sequence = dna.sequence[:mutation_site] + new_base + dna.sequence[mutation_site + 1:]
            print(f"Off-target mutation occurred at position {mutation_site}")
            return DNA(new_sequence)
        return dna
    