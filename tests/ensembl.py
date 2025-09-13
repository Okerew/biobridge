import unittest
from unittest.mock import patch
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# Import the classes from your modules
from biobridge.genes.dna import DNA
from biobridge.genes.rna import RNA
from biobridge.blocks.protein import Protein
from biobridge.parsers.ensembl import EnsemblParser

class TestEnsemblParser(unittest.TestCase):

    @patch('Bio.SeqIO.parse')
    def setUp(self, mock_seqio_parse):
        # Creating mock records
        mock_seq = Seq("ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG")
        mock_feature = SeqFeature(
            FeatureLocation(0, 9), type="CDS",
            qualifiers={
                "gene": ["mock_gene"],
                "protein_id": ["mock_protein_id"],
                "protein": "mock_protein",
                "translation": ["MAMAPRTEINSEQ"],
                "product": ["mock_product"],
                "note": ["mock_note"]
            }
        )
        mock_record = SeqRecord(mock_seq, id="mock_id", name="mock_name", description="mock_description")
        mock_record.features = [mock_feature]

        # Mocking SeqIO.parse to return our mock record
        mock_seqio_parse.return_value = [mock_record]

        self.parser = EnsemblParser("mock_file_path")

    def test_parse_records(self):
        parsed_elements = self.parser.parse_records()

        self.assertEqual(len(parsed_elements), 3)
        self.assertIsInstance(parsed_elements[0], Protein)
        self.assertIsInstance(parsed_elements[1], DNA)
        self.assertIsInstance(parsed_elements[2], RNA)

        protein = parsed_elements[0]
        dna = parsed_elements[1]
        rna = parsed_elements[2]

        # Test Protein
        self.assertEqual(protein.id, "mock_protein_id")
        self.assertEqual(protein.sequence, "MAMAPRTEINSEQ")
        self.assertEqual(protein.product, "mock_product")
        self.assertEqual(protein.notes, ["mock_note"])

    def test_get_metadata(self):
        metadata = self.parser.get_metadata()

        self.assertEqual(len(metadata), 1)
        self.assertEqual(metadata[0]['id'], "mock_id")
        self.assertEqual(metadata[0]['name'], "mock_name")
        self.assertEqual(metadata[0]['description'], "mock_description")
        self.assertIn('annotations', metadata[0])


if __name__ == '__main__':
    unittest.main()
