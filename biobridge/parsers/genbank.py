from Bio import SeqIO
from Bio.SeqFeature import FeatureLocation

from biobridge.blocks.protein import Protein
from biobridge.genes.dna import DNA
from biobridge.genes.rna import RNA


class GenbankParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.records = list(SeqIO.parse(self.file_path, "genbank"))

    def parse_records(self):
        parsed_elements = []
        for record in self.records:
            sequence = str(record.seq)
            if record.features:
                for feature in record.features:
                    if feature.type == "CDS":
                        protein_seq = feature.qualifiers.get("translation", [""])[0]
                        if protein_seq:
                            protein = self.create_protein(feature, protein_seq)
                            parsed_elements.append(protein)

                        dna = self.create_dna(feature, sequence)
                        parsed_elements.append(dna)

                        rna = self.create_rna(feature, sequence)
                        parsed_elements.append(rna)
            else:
                # If no features, create a DNA object for the entire sequence
                dna = DNA(sequence)
                parsed_elements.append(dna)

        return parsed_elements

    def create_protein(self, feature, protein_seq):
        protein_name = feature.qualifiers.get("product", ["Unknown"])[0]
        protein_id = feature.qualifiers.get("protein_id", ["Unknown"])[0]
        protein = Protein(protein_name, protein_seq, id=protein_id)

        return protein

    def create_dna(self, feature, full_sequence):
        start = feature.location.start
        end = feature.location.end

        if isinstance(feature.location, FeatureLocation):
            dna_seq = feature.location.extract(full_sequence)
        else:
            dna_seq = full_sequence[start:end]

        dna = DNA(str(dna_seq))
        gene_name = feature.qualifiers.get("gene", ["Unknown"])[0]
        dna.add_gene(gene_name, 0, len(dna_seq))

        return dna

    def create_rna(self, feature, full_sequence):
        start = feature.location.start
        end = feature.location.end

        if isinstance(feature.location, FeatureLocation):
            rna_seq = feature.location.extract(full_sequence)
        else:
            rna_seq = full_sequence[start:end]

        # Convert T to U for RNA
        rna_seq = rna_seq.replace("T", "U")

        rna = RNA(str(rna_seq))
        return rna

    def get_metadata(self):
        metadata = []
        for record in self.records:
            record_metadata = {
                "id": record.id,
                "name": record.name,
                "description": record.description,
                "annotations": record.annotations,
            }
            metadata.append(record_metadata)
        return metadata
