import pandas as pd
from biobridge.genes.dna import DNA
from biobridge.genes.rna import RNA
from biobridge.blocks.protein import Protein


class CSVParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = pd.read_csv(self.file_path)

    def parse_records(self):
        parsed_elements = []
        for index, row in self.data.iterrows():
            sequence = row['sequence']
            sequence_type = row['type']

            if sequence_type == 'DNA':
                dna = DNA(sequence)
                parsed_elements.append(dna)
            elif sequence_type == 'RNA':
                rna = RNA(sequence)
                parsed_elements.append(rna)
            elif sequence_type == 'Protein':
                protein = Protein(row['id'], sequence)
                parsed_elements.append(protein)

        return parsed_elements
