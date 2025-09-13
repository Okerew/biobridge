import unittest
from biobridge.tools.sequencer import DNASequencer


class TestDNASequencer(unittest.TestCase):

    def test_initialization(self):
        sequencer = DNASequencer(error_rate=0.002, read_length=50)
        self.assertEqual(sequencer.error_rate, 0.002)
        self.assertEqual(sequencer.read_length, 50)

    def test_sequence_length(self):
        dna = "ATCG" * 50  # 200 nucleotides
        sequencer = DNASequencer(read_length=100)
        reads = sequencer.sequence(dna)
        self.assertEqual(len(reads), 2)
        self.assertTrue(all(len(read) == 100 for read in reads))

    def test_introduce_errors(self):
        dna = "ATCG" * 25  # 100 nucleotides
        sequencer = DNASequencer(error_rate=1.0, read_length=100)  # Force errors
        read = sequencer.sequence(dna)[0]
        self.assertNotEqual(dna, read)  # Ensure the read is altered

    def test_assemble(self):
        dna = "ATCG" * 25
        sequencer = DNASequencer(read_length=10)
        reads = sequencer.sequence(dna)
        assembled_dna = sequencer.assemble(reads)

    def test_find_overlap(self):
        seq1 = "ATCGATCG"
        seq2 = "TCGATCGA"
        sequencer = DNASequencer()
        overlap = sequencer._find_overlap(seq1, seq2)
        self.assertEqual(overlap, 7)

    def test_analyze_quality(self):
        dna = "ATCG" * 50
        sequencer = DNASequencer(read_length=100)
        reads = sequencer.sequence(dna)
        assembled_dna = sequencer.assemble(reads)
        accuracy, coverage, avg_read_length = sequencer.analyze_quality(dna, assembled_dna)
        self.assertEqual(avg_read_length, 100)


if __name__ == '__main__':
    unittest.main()
