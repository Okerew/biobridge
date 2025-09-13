import unittest
from biobridge.genes.chromosome import Chromosome, DNA
from biobridge.definitions.cells.germ_cell import GermCell


class TestGermCell(unittest.TestCase):
    def setUp(self):
        self.germ_cell = GermCell("TestCell")

    def test_initialization(self):
        self.assertEqual(self.germ_cell.name, "TestCell")
        self.assertEqual(self.germ_cell.cell_type, "germ")
        self.assertEqual(self.germ_cell.ploidy, 2)
        self.assertEqual(self.germ_cell.meiosis_stage, "interphase")
        self.assertIsNone(self.germ_cell.gamete_type)

    def test_undergo_meiosis(self):
        self.germ_cell.chromosomes = [Chromosome(dna=DNA("ATCG" * 1000), name="Chromosome1"), Chromosome(dna=DNA("ATCG" * 1000), name="Chromosome2")]
        gametes = self.germ_cell.undergo_meiosis()
        self.assertEqual(len(gametes), 4)
        self.assertEqual(gametes[0].ploidy, 1)
        self.assertEqual(gametes[0].meiosis_stage, "completed")
        self.assertEqual(self.germ_cell.meiosis_stage, "completed")

    def test_form_synaptonemal_complex(self):
        self.germ_cell.meiosis_stage = "prophase I"
        self.germ_cell.chromosomes = [Chromosome(dna=DNA("ATCG" * 1000), name="Chromosome1"), Chromosome(dna=DNA("ATCG" * 1000), name="Chromosome2")]
        self.germ_cell.form_synaptonemal_complex()
        self.assertEqual(len(self.germ_cell.synaptonemal_complex), 1)

    def test_differentiate_gamete(self):
        self.germ_cell.differentiate_gamete("sperm")
        self.assertEqual(self.germ_cell.gamete_type, "sperm")
        self.assertEqual(self.germ_cell.cell_type, "sperm_cell")
        self.assertIn("acrosome", self.germ_cell.organelles)
        self.assertIn("flagellum", self.germ_cell.organelles)

    def test_describe(self):
        description = self.germ_cell.describe()
        self.assertIsInstance(description, str)

    def test_to_dict(self):
        cell_dict = self.germ_cell.to_dict()
        self.assertIsInstance(cell_dict, dict)
        self.assertEqual(cell_dict['name'], "TestCell")

    def test_from_dict(self):
        cell_dict = self.germ_cell.to_dict()
        new_germ_cell = GermCell.from_dict(cell_dict)
        self.assertEqual(new_germ_cell.name, "TestCell")


if __name__ == "__main__":
    unittest.main()
