import unittest
from biobridge.tools.bip import BioinformaticsPipeline
from biobridge.genes.dna import DNA
from biobridge.blocks.protein import Protein
from biobridge.blocks.cell import Cell


class TestBioinformaticsPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = BioinformaticsPipeline()

    def test_align_sequences(self):
        seq1 = "ATCG"
        seq2 = "ATCG"
        aligned1, aligned2 = self.pipeline.align_sequences(seq1, seq2)
        self.assertEqual(aligned1, "ATCG")
        self.assertEqual(aligned2, "ATCG")

        seq1 = "ATCG"
        seq2 = "TCG"
        aligned1, aligned2 = self.pipeline.align_sequences(seq1, seq2)
        self.assertEqual(aligned1, "ATCG")
        self.assertEqual(aligned2, "-TCG")

    def test_transcribe_dna(self):
        dna_sequence = "ATCG"
        rna_sequence = self.pipeline.transcribe_dna(dna_sequence)
        self.assertEqual(rna_sequence, "AUCG")

    def test_translate_rna(self):
        rna_sequence = "AUGGCCUAA"
        protein_sequence = self.pipeline.translate_rna(rna_sequence)
        self.assertEqual(protein_sequence, "MA")

    def test_find_mutations(self):
        seq1 = "ATCG"
        seq2 = "ACCG"
        mutations = self.pipeline.find_mutations(seq1, seq2)
        self.assertEqual(mutations, [(1, 'T', 'C')])

    def test_simulate_evolution(self):
        dna = DNA("ATCG")
        evolved_dna = self.pipeline.simulate_evolution(dna, generations=10, mutation_rate=0.1)
        self.assertIsInstance(evolved_dna, DNA)
        self.assertEqual(len(evolved_dna.sequence), 4)

    def test_analyze_protein_interactions(self):
        protein = Protein("TestProtein", "ARNDCEQGHILKMFPSTWYV")
        protein.add_binding("ReceptorA", "high")
        cell = Cell("TestCell")
        cell.add_receptor(protein)

        analysis = self.pipeline.analyze_protein_interactions(protein, cell)
        self.assertIn("TestProtein", analysis)
        self.assertIn("TestCell", analysis)

if __name__ == "__main__":
    unittest.main()
    
