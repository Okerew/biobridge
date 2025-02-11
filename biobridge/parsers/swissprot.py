from Bio import SeqIO
from biobridge.blocks.protein import Protein


class SwissProtParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.records = []

        # Try parsing as Swiss-Prot format
        try:
            self.records = list(SeqIO.parse(self.file_path, "swiss"))
        except ValueError as e:
            print(f"Error parsing Swiss-Prot file: {e}")
            # If Swiss-Prot format fails, try UniProt XML format
            try:
                self.records = list(SeqIO.parse(self.file_path, "uniprot-xml"))
            except ValueError as e:
                print(f"Error parsing UniProt XML file: {e}")
                raise ValueError(
                    f"Unable to parse file {self.file_path}. Ensure it's a valid Swiss-Prot or UniProt XML file.")

    def parse_records(self):
        parsed_proteins = []
        for record in self.records:
            protein = self.create_protein(record)
            parsed_proteins.append(protein)
        return parsed_proteins

    def create_protein(self, record):
        unique_id = record.id

        protein = Protein(name=str(record.name), sequence=str(record.seq), id=unique_id)

        protein.original_id = record.id  # Store the original ID from the record
        protein.name = record.name
        protein.description = record.description

        # Add additional information
        protein.organism = record.annotations.get("organism", "Unknown")
        protein.gene_name = record.annotations.get("gene_name", "Unknown")
        protein.function = record.annotations.get("comment_function", "Unknown")

        # Add features (like domains, binding sites, etc.)
        protein.features = []
        for feature in record.features:
            if feature.type != "chain":  # Exclude the 'chain' feature as it typically represents the entire sequence
                protein.features.append({
                    "type": feature.type,
                    "location": (feature.location.start, feature.location.end),
                    "qualifiers": feature.qualifiers
                })

        return protein

    def get_metadata(self):
        metadata = []
        for record in self.records:
            record_metadata = {
                "id": record.id,
                "name": record.name,
                "description": record.description,
                "annotations": record.annotations
            }
            metadata.append(record_metadata)
        return metadata
