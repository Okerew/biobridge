import unittest
from unittest.mock import patch
from biobridge.definitions.organisms.bacteria import Bacteria, DNA

class TestBacteria(unittest.TestCase):
    def setUp(self):
        # Create a simple DNA object for testing
        self.test_dna = DNA(sequence="ATCG")
        self.test_plasmid = DNA(sequence="GCTA")

        # Create a Bacteria object for testing
        self.bacteria = Bacteria(
            name="TestBacteria",
            species="TestSpecies",
            gram_stain="positive",
            shape="rod",
            motility=True,
            cell_wall_thickness=20.0,
            plasmids=[self.test_plasmid],
            flagella=True,
            pili=True,
            capsule=True,
            antibiotic_resistance=["penicillin"],
            chromosomes=[self.test_dna],
            dna=self.test_dna,
            health=100,
            metabolism_rate=1.0,
            ph=7.0,
            osmolarity=0.9,
            ion_concentrations={"Na+": 10},
            structural_integrity=1.0,
            mutation_count=0,
            growth_rate=1.0,
            repair_rate=1.0
        )

    def test_initialization(self):
        self.assertEqual(self.bacteria.name, "TestBacteria")
        self.assertEqual(self.bacteria.species, "TestSpecies")
        self.assertEqual(self.bacteria.gram_stain, "positive")
        self.assertEqual(self.bacteria.shape, "rod")
        self.assertTrue(self.bacteria.motility)
        self.assertEqual(self.bacteria.cell_wall_thickness, 20.0)
        self.assertEqual(len(self.bacteria.plasmids), 1)
        self.assertTrue(self.bacteria.flagella)
        self.assertTrue(self.bacteria.pili)
        self.assertTrue(self.bacteria.capsule)
        self.assertEqual(self.bacteria.antibiotic_resistance, ["penicillin"])
        self.assertEqual(self.bacteria.binary_fission_count, 0)

    def test_conjugation(self):
        recipient = Bacteria(
            name="Recipient",
            species="RecipientSpecies",
            gram_stain="negative",
            shape="spherical",
            motility=False,
            cell_wall_thickness=15.0,
            pili=True,
        )
        result = self.bacteria.conjugate(recipient)
        self.assertTrue(result)
        self.assertEqual(len(recipient.plasmids), 1)

    def test_binary_fission(self):
        daughter = self.bacteria.binary_fission()
        self.assertEqual(daughter.name, "TestBacteria_daughter_1")
        self.assertEqual(daughter.species, "TestSpecies")
        self.assertEqual(daughter.gram_stain, "positive")
        self.assertEqual(daughter.shape, "rod")
        self.assertTrue(daughter.motility)
        self.assertEqual(daughter.cell_wall_thickness, 20.0)
        self.assertEqual(len(daughter.plasmids), 1)
        self.assertTrue(daughter.flagella)
        self.assertTrue(daughter.pili)
        self.assertTrue(daughter.capsule)
        self.assertEqual(daughter.antibiotic_resistance, ["penicillin"])
        self.assertEqual(self.bacteria.binary_fission_count, 1)

    def test_form_biofilm(self):
        result = self.bacteria.form_biofilm("surface")
        self.assertEqual(result, "TestBacteria has formed a biofilm on the surface.")

    def test_respond_to_antibiotic(self):
        result = self.bacteria.respond_to_antibiotic("penicillin")
        self.assertEqual(result, "TestBacteria is resistant to penicillin. Minor health impact.")
        self.assertEqual(self.bacteria.health, 90)

        result = self.bacteria.respond_to_antibiotic("ampicillin")
        self.assertEqual(result, "TestBacteria is not resistant to ampicillin. Major health impact.")
        self.assertEqual(self.bacteria.health, 40)

    @patch('random.random')
    def test_mutate(self, mock_random):
        mock_random.return_value = 0.05  # Force mutation
        self.bacteria.mutate()
        self.assertEqual(len(self.bacteria.antibiotic_resistance), 2)

    def test_describe(self):
        description = self.bacteria.describe()
        self.assertIn("Species: TestSpecies", description)
        self.assertIn("Gram Stain: positive", description)
        self.assertIn("Shape: rod", description)
        self.assertIn("Motility: Yes", description)
        self.assertIn("Antibiotic Resistance: penicillin", description)

    def test_to_dict_and_from_dict(self):
        bacteria_dict = self.bacteria.to_dict()
        new_bacteria = Bacteria.from_dict(bacteria_dict)
        self.assertEqual(new_bacteria.name, "TestBacteria")
        self.assertEqual(new_bacteria.species, "TestSpecies")
        self.assertEqual(new_bacteria.gram_stain, "positive")
        self.assertEqual(new_bacteria.shape, "rod")
        self.assertTrue(new_bacteria.motility)
        self.assertEqual(new_bacteria.cell_wall_thickness, 20.0)
        self.assertEqual(len(new_bacteria.plasmids), 1)
        self.assertTrue(new_bacteria.flagella)
        self.assertTrue(new_bacteria.pili)
        self.assertTrue(new_bacteria.capsule)
        self.assertEqual(new_bacteria.antibiotic_resistance, ["penicillin"])
        self.assertEqual(new_bacteria.binary_fission_count, 0)

if __name__ == "__main__":
    unittest.main()
