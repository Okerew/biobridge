import random


class mRNA:
    def __init__(self, sequence):
        """
        Initialize a new mRNA object.

        :param sequence: The nucleotide sequence of the mRNA strand
        """
        self.sequence = sequence.upper().replace('T', 'U')
        self.cap = "m7G"  # 7-methylguanosine cap
        self.poly_a_tail = "A" * 200  # Typical poly-A tail length
        self.utr_5 = ""  # 5' untranslated region
        self.utr_3 = ""  # 3' untranslated region
        self.coding_sequence = ""
        self.ribosome_binding_sites = []

    def add_cap(self):
        """Add a 7-methylguanosine cap to the 5' end of the mRNA."""
        self.sequence = self.cap + self.sequence

    def add_poly_a_tail(self, length=200):
        """Add a poly-A tail to the 3' end of the mRNA."""
        self.poly_a_tail = "A" * length
        self.sequence += self.poly_a_tail

    def set_utrs(self, utr_5, utr_3):
        """Set the 5' and 3' untranslated regions."""
        self.utr_5 = utr_5
        self.utr_3 = utr_3
        self.sequence = self.utr_5 + self.sequence + self.utr_3

    def find_start_codon(self):
        """Find the start codon (AUG) in the mRNA sequence."""
        return self.sequence.find('AUG')

    def find_stop_codons(self):
        """Find all stop codons (UAA, UAG, UGA) in the mRNA sequence."""
        stop_codons = ['UAA', 'UAG', 'UGA']
        return [i for i in range(0, len(self.sequence) - 2, 3)
                if self.sequence[i:i + 3] in stop_codons]

    def set_coding_sequence(self):
        """Set the coding sequence based on start and stop codons."""
        start = self.find_start_codon()
        if start != -1:
            stops = self.find_stop_codons()
            stop = next((s for s in stops if s > start), -1)
            if stop != -1:
                self.coding_sequence = self.sequence[start:stop + 3]

    def transcribe_to_mrna(self):
        """
        Simulate transcription of DNA to mRNA (replace T with U if any T is present).

        :return: The mRNA sequence
        """
        return self.sequence.replace('T', 'U')

    def reverse_transcribe(self):
        """
        Reverse transcribe the mRNA sequence into DNA (replace U with T).

        :return: The DNA sequence corresponding to the mRNA
        """
        return self.sequence.replace('U', 'T')

    def translate(self):
        """Translate the coding sequence into a protein sequence."""
        if not self.coding_sequence:
            self.set_coding_sequence()

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
        for i in range(0, len(self.coding_sequence) - 2, 3):
            codon = self.coding_sequence[i:i + 3]
            amino_acid = codon_table.get(codon, 'X')  # 'X' for unknown amino acid
            if amino_acid == '*':
                break  # Stop translation at stop codon
            protein += amino_acid
        return protein

    def find_kozak_sequence(self):
        """Find Kozak consensus sequence near start codon."""
        start = self.find_start_codon()
        if start >= 4 and start + 4 < len(self.sequence):
            return self.sequence[start - 4:start + 4]
        return None

    def add_ribosome_binding_site(self, position):
        """Add a ribosome binding site at the specified position."""
        self.ribosome_binding_sites.append(position)

    def simulate_degradation(self, rate=0.01):
        """Simulate mRNA degradation by shortening the poly-A tail."""
        degraded_length = max(0, len(self.poly_a_tail) - int(len(self.poly_a_tail) * rate))
        self.poly_a_tail = "A" * degraded_length
        self.sequence = self.sequence[:-len(self.poly_a_tail)] + self.poly_a_tail

    def get_gc_content(self):
        """Calculate the GC content of the mRNA sequence."""
        gc_count = self.sequence.count('G') + self.sequence.count('C')
        return gc_count / len(self.sequence)

    def find_motifs(self, motif):
        """Find all occurrences of a specific motif in the mRNA sequence."""
        return [i for i in range(len(self.sequence)) if self.sequence.startswith(motif, i)]

    def simulate_alternative_splicing(self, exon_ranges, base_inclusion_prob=0.7):
        """
        Simulate alternative splicing using a more sophisticated algorithm.

        :param exon_ranges: List of tuples (start, end) for each exon
        :param base_inclusion_prob: Base probability of including any exon
        """
        exons = [self.sequence[start:end] for start, end in exon_ranges]

        # Calculate exon weights based on length (longer exons are slightly more likely to be included)
        exon_weights = [len(exon) ** 0.5 for exon in exons]

        # Normalize weights
        total_weight = sum(exon_weights)
        normalized_weights = [w / total_weight for w in exon_weights]

        # Determine inclusion probabilities
        inclusion_probs = [base_inclusion_prob * (1 + 0.5 * (w - 1 / len(exons))) for w in normalized_weights]

        # Ensure first and last exons are always included (for simplicity)
        inclusion_probs[0] = 1
        inclusion_probs[-1] = 1

        # Choose exons based on their inclusion probabilities
        included_exons = []
        for i, exon in enumerate(exons):
            if random.random() < inclusion_probs[i]:
                included_exons.append(exon)

        # Ensure at least two exons are included (first and last)
        if len(included_exons) < 2:
            included_exons = [exons[0], exons[-1]]

        # Update the mRNA sequence
        self.sequence = ''.join(included_exons)

        # Update coding sequence, UTRs, etc. as necessary
        self.set_coding_sequence()

        return included_exons

    def __str__(self):
        """Return a string representation of the mRNA."""
        return (f"5' Cap: {self.cap}\n"
                f"5' UTR: {self.utr_5}\n"
                f"Coding Sequence: {self.coding_sequence}\n"
                f"3' UTR: {self.utr_3}\n"
                f"Poly-A Tail: {self.poly_a_tail}")

    def __len__(self):
        """Return the total length of the mRNA, including cap and poly-A tail."""
        return len(self.sequence) + len(self.cap) + len(self.poly_a_tail)