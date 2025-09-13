from Bio import SeqIO
from biobridge.genes.dna import DNA
from biobridge.genes.rna import RNA
from biobridge.blocks.protein import Protein


class FastaParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.records = list(SeqIO.parse(self.file_path, "fasta"))

    def parse_records(self):
        parsed_elements = []
        for record in self.records:
            sequence = str(record.seq)
            element = self.create_element(record.id, sequence)
            parsed_elements.append(element)
        return parsed_elements

    def create_element(self, identifier, sequence):
        # Attempt to determine the type of sequence
        if set(sequence).issubset(set("ACGTU")):
            if 'U' in sequence:
                return RNA(sequence)
            else:
                return DNA(sequence, [(identifier, 0, len(sequence))])
        else:
            return Protein(identifier, sequence)

    def get_metadata(self):
        metadata = []
        for record in self.records:
            record_metadata = {
                "id": record.id,
                "description": record.description,
            }
            metadata.append(record_metadata)
        return metadata