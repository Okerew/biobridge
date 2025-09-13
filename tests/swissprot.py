import unittest
from unittest.mock import patch, Mock
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from biobridge.blocks.protein import Protein
from biobridge.parsers.swissprot import SwissProtParser

class TestSwissProtParser(unittest.TestCase):

    def setUp(self):
        self.mock_file_path = "mock_file.dat"
        self.mock_record = SeqRecord(
            Seq("MAKAGAMQ"),
            id="P12345",
            name="TEST_PROTEIN",
            description="Test protein description",
            annotations={
                "organism": "Test Organism",
                "gene_name": "TEST",
                "comment_function": "Test function"
            },
            features=[
                Mock(type="domain", location=Mock(start=0, end=4), qualifiers={"note": "Test domain"}),
                Mock(type="binding site", location=Mock(start=5, end=8), qualifiers={"note": "Test binding site"})
            ]
        )
        print(self.mock_record)

    @patch('Bio.SeqIO.parse')
    def test_init_swiss_prot(self, mock_parse):
        mock_parse.return_value = [self.mock_record]
        parser = SwissProtParser(self.mock_file_path)
        self.assertEqual(len(parser.records), 1)
        mock_parse.assert_called_once_with(self.mock_file_path, "swiss")

    @patch('Bio.SeqIO.parse')
    def test_init_uniprot_xml(self, mock_parse):
        mock_parse.side_effect = [ValueError(), [self.mock_record]]
        parser = SwissProtParser(self.mock_file_path)
        self.assertEqual(len(parser.records), 1)
        mock_parse.assert_called_with(self.mock_file_path, "uniprot-xml")

    @patch('Bio.SeqIO.parse')
    def test_init_invalid_file(self, mock_parse):
        mock_parse.side_effect = ValueError()
        with self.assertRaises(ValueError):
            SwissProtParser(self.mock_file_path)

    @patch('Bio.SeqIO.parse')
    def test_parse_records(self, mock_parse):
        mock_parse.return_value = [self.mock_record]
        parser = SwissProtParser(self.mock_file_path)
        proteins = parser.parse_records()
        self.assertEqual(len(proteins), 1)
        self.assertIsInstance(proteins[0], Protein)

    @patch('Bio.SeqIO.parse')
    def test_create_protein(self, mock_parse):
        mock_parse.return_value = [self.mock_record]
        parser = SwissProtParser(self.mock_file_path)
        protein = parser.create_protein(self.mock_record)
        self.assertEqual(protein.id, "P12345")
        self.assertEqual(protein.sequence, "MAKAGAMQ")
        self.assertEqual(protein.name, "TEST_PROTEIN")
        self.assertEqual(protein.description, "Test protein description")
        self.assertEqual(protein.organism, "Test Organism")
        self.assertEqual(protein.gene_name, "TEST")
        self.assertEqual(protein.function, "Test function")
        self.assertEqual(len(protein.features), 2)

    @patch('Bio.SeqIO.parse')
    def test_get_metadata(self, mock_parse):
        mock_parse.return_value = [self.mock_record]
        parser = SwissProtParser(self.mock_file_path)
        metadata = parser.get_metadata()
        self.assertEqual(len(metadata), 1)
        self.assertEqual(metadata[0]['id'], "P12345")
        self.assertEqual(metadata[0]['name'], "TEST_PROTEIN")
        self.assertEqual(metadata[0]['description'], "Test protein description")
        self.assertIn('annotations', metadata[0])

if __name__ == '__main__':
    unittest.main()