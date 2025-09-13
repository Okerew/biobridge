import json

from biobridge.genes.rna import RNA


class tRNA(RNA):
    def __init__(self, sequence, anticodon, amino_acid):
        """
        Initialize a new tRNA object.

        :param sequence: The nucleotide sequence of the tRNA strand
        :param anticodon: The anticodon sequence of the tRNA
        :param amino_acid: The amino acid carried by the tRNA
        """
        super().__init__(sequence)
        self.anticodon = anticodon.upper()
        self.amino_acid = amino_acid

    def get_anticodon(self):
        """
        Return the anticodon sequence of the tRNA.

        :return: The anticodon sequence
        """
        return self.anticodon

    def get_amino_acid(self):
        """
        Return the amino acid carried by the tRNA.

        :return: The amino acid
        """
        return self.amino_acid

    def matches_codon(self, codon):
        """
        Check if the tRNA anticodon matches the given codon with wobble base pairing.

        :param codon: The codon sequence to check
        :return: True if the anticodon matches the codon, False otherwise
        """
        if len(codon) != 3 or len(self.anticodon) != 3:
            return False

        # Check the first two positions for exact match
        if self.anticodon[0] != codon[2] or self.anticodon[1] != codon[1]:
            return False

        # Check the third position with wobble base pairing
        anticodon_third = self.anticodon[2]
        codon_third = codon[0]

        if anticodon_third == codon_third:
            return True
        elif anticodon_third == "A" and codon_third == "U":
            return True
        elif anticodon_third == "G" and (codon_third == "C" or codon_third == "U"):
            return True

        return False

    def bind_to_mrna(self, mrna_sequence, start_index):
        """
        Simulate binding of the tRNA to an mRNA sequence at a specific start index.

        :param mrna_sequence: The mRNA sequence to bind to
        :param start_index: The starting index in the mRNA sequence to check for binding
        :return: True if the tRNA binds to the mRNA, False otherwise
        """
        codon = mrna_sequence[start_index : start_index + 3]
        if self.matches_codon(codon):
            print(
                f"tRNA with anticodon {self.anticodon} binds to codon {codon} at index {start_index}."
            )
            return True
        else:
            print(
                f"tRNA with anticodon {self.anticodon} does not bind to codon {codon} at index {start_index}."
            )
            return False

    def to_dict(self):
        """
        Convert the tRNA object to a dictionary.

        :return: Dictionary representation of the tRNA
        """
        return {
            "sequence": self.sequence,
            "anticodon": self.anticodon,
            "amino_acid": self.amino_acid,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a tRNA object from a dictionary.

        :param data: Dictionary containing tRNA data
        :return: tRNA object
        """
        return cls(data["sequence"], data["anticodon"], data["amino_acid"])

    def to_json(self):
        """
        Convert the tRNA object to a JSON string.

        :return: JSON string representation of the tRNA
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str):
        """
        Create a tRNA object from a JSON string.

        :param json_str: JSON string containing tRNA data
        :return: tRNA object
        """
        return cls.from_dict(json.loads(json_str))

    def __str__(self):
        """
        Return a string representation of the tRNA.
        """
        return f"tRNA Sequence: {self.sequence}, Anticodon: {self.anticodon}, Amino Acid: {self.amino_acid}"
