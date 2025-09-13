import unittest
from biobridge.genes.dna import DNA
from matplotlib.pyplot import close as plt_close
from biobridge.genes.chromosome import Chromosome


class TestChromosome(unittest.TestCase):

    def setUp(self):
        # Create a mock DNA sequence for testing
        self.dna_sequence = "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        self.dna = DNA(self.dna_sequence)
        self.chromosome = Chromosome(self.dna, "TestChromosome")

    def test_initialization(self):
        self.assertEqual(self.chromosome.name, "TestChromosome")
        self.assertIsNotNone(self.chromosome.p_arm)
        self.assertIsNotNone(self.chromosome.q_arm)
        self.assertEqual(self.chromosome.centromere_position, len(self.dna) // 2)
        self.assertEqual(self.chromosome.telomere_length, 100)
        self.assertEqual(self.chromosome.chromosome_type, "Metacentric")
        self.assertIsNone(self.chromosome.satellite_dna)
        self.assertEqual(self.chromosome.constrictions, [])

    def test_add_band(self):
        self.chromosome.add_band('p', 0, 10, 'dark')
        self.chromosome.add_band('q', 10, 20, 'light')
        self.assertEqual(self.chromosome.p_arm.bands, [(0, 10, 'dark')])
        self.assertEqual(self.chromosome.q_arm.bands, [(10, 20, 'light')])

    def test_replicate(self):
        new_chromosome = self.chromosome.replicate()
        self.assertEqual(new_chromosome.name, "TestChromosome_copy")
        self.assertEqual(new_chromosome.centromere_position, self.chromosome.centromere_position)
        self.assertEqual(new_chromosome.telomere_length, self.chromosome.telomere_length)
        self.assertEqual(new_chromosome.chromosome_type, self.chromosome.chromosome_type)

    def test_crossover(self):
        other_dna = DNA("TGCA" * 17)
        other_chromosome = Chromosome(other_dna, "OtherChromosome")
        crossover_points = [10, 20]
        new_chromosome = self.chromosome.crossover(other_chromosome, crossover_points)
        self.assertNotEqual(self.chromosome.get_sequence(), new_chromosome.get_sequence())
        self.assertEqual(new_chromosome.name, "TestChromosome_crossover")

    def test_mutate(self):
        original_sequence = self.chromosome.get_sequence()
        self.chromosome.mutate()
        new_sequence = self.chromosome.get_sequence()
        print(original_sequence, new_sequence)

    def test_invert(self):
        original_sequence = self.chromosome.get_sequence()
        self.chromosome.invert(10, 20)
        new_sequence = self.chromosome.get_sequence()
        self.assertNotEqual(original_sequence, new_sequence)

    def test_transpose(self):
        original_sequence = self.chromosome.get_sequence()
        self.chromosome.transpose(10, 20, 30)
        new_sequence = self.chromosome.get_sequence()
        self.assertNotEqual(original_sequence, new_sequence)

    def test_visualize(self):
        self.chromosome.visualize()
        plt_close()  # Close the plot to avoid displaying it during tests

    def test_compare(self):
        other_dna = DNA("TGCA" * 17)
        other_chromosome = Chromosome(other_dna, "OtherChromosome")
        similarity = self.chromosome.compare(other_chromosome)
        self.assertLess(similarity, 1.0)

    def test_to_dict(self):
        chromosome_dict = self.chromosome.to_dict()
        self.assertEqual(chromosome_dict['name'], "TestChromosome")
        self.assertEqual(chromosome_dict['centromere_position'], len(self.dna) // 2)
        self.assertEqual(chromosome_dict['telomere_length'], 100)
        self.assertEqual(chromosome_dict['chromosome_type'], "Metacentric")
        self.assertIsNone(chromosome_dict['satellite_dna'])
        self.assertEqual(chromosome_dict['constrictions'], [])

    def test_from_dict(self):
        chromosome_dict = self.chromosome.to_dict()
        new_chromosome = Chromosome.from_dict(chromosome_dict)
        self.assertEqual(new_chromosome.name, "TestChromosome")
        self.assertEqual(new_chromosome.centromere_position, len(self.dna) // 2)
        self.assertEqual(new_chromosome.telomere_length, 100)
        self.assertEqual(new_chromosome.chromosome_type, "Metacentric")
        self.assertIsNone(new_chromosome.satellite_dna)
        self.assertEqual(new_chromosome.constrictions, [])


if __name__ == '__main__':
    unittest.main()
